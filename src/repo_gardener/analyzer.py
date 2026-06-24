"""Core repository analysis logic. Produces Garden Scores and structured reports."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import git
from git.exc import InvalidGitRepositoryError

from .scorers import DimensionScore, compute_dimensions


@dataclass
class RepoAnalysis:
    """Complete analysis result for a repository."""

    path: Path
    repo_name: str | None = None
    remote_url: str | None = None

    garden_score: int = 0
    dimensions: list[DimensionScore] = field(default_factory=list)

    languages: list[str] = field(default_factory=list)
    file_count: int = 0
    commit_count: int = 0

    has_readme: bool = False
    has_license: bool = False
    has_tests: bool = False
    has_gitignore: bool = False
    has_pyproject: bool = False
    has_requirements: bool = False

    suggestions: list[str] = field(default_factory=list)
    details: dict[str, Any] = field(default_factory=dict)


def analyze_repository(path: Path, *, verbose: bool = False) -> RepoAnalysis:
    """Analyze the given directory as a Git repository."""
    path = path.resolve()

    analysis = RepoAnalysis(path=path)

    # Try to open as git repo
    try:
        repo = git.Repo(path, search_parent_directories=True)
        git_root = Path(repo.working_dir)
        analysis.path = git_root  # Normalize to repo root

        # Basic repo metadata
        analysis.repo_name = git_root.name
        if repo.remotes:
            try:
                analysis.remote_url = repo.remotes.origin.url
            except Exception:
                pass

        # Commit count (safe for empty repos / shallow clones)
        analysis.commit_count = 0
        try:
            if repo.head.is_valid():
                analysis.commit_count = len(list(repo.iter_commits(max_count=500)))
        except Exception:
            analysis.commit_count = 0

    except InvalidGitRepositoryError:
        # Still analyze as a plain directory (useful for non-git projects too)
        analysis.repo_name = path.name
        repo = None
    except Exception as e:
        raise RuntimeError(f"Failed to inspect git repository: {e}") from e

    # Walk the filesystem to gather facts
    facts = _gather_facts(analysis.path)

    analysis.file_count = facts["file_count"]
    analysis.languages = facts["languages"]
    analysis.has_readme = facts["has_readme"]
    analysis.has_license = facts["has_license"]
    analysis.has_tests = facts["has_tests"]
    analysis.has_gitignore = facts["has_gitignore"]
    analysis.has_pyproject = facts["has_pyproject"]
    analysis.has_requirements = facts["has_requirements"]

    # Compute the Garden Score dimensions
    dimensions = compute_dimensions(analysis, facts, repo=repo)
    analysis.dimensions = dimensions

    # Overall score (weighted average)
    if dimensions:
        total_weight = sum(d.weight for d in dimensions)
        weighted = sum(d.score * d.weight for d in dimensions)
        analysis.garden_score = int(round(weighted / total_weight)) if total_weight > 0 else 0
    else:
        analysis.garden_score = 0

    # Generate actionable suggestions
    analysis.suggestions = _generate_suggestions(analysis, facts)

    if verbose:
        analysis.details = {
            "top_extensions": facts.get("top_extensions", {}),
            "has_src_layout": facts.get("has_src_layout", False),
            "has_ci": facts.get("has_ci", False),
        }

    return analysis


# ---------- helpers ----------

LANGUAGE_MAP = {
    ".py": "Python",
    ".js": "JavaScript",
    ".ts": "TypeScript",
    ".jsx": "JavaScript",
    ".tsx": "TypeScript",
    ".go": "Go",
    ".rs": "Rust",
    ".java": "Java",
    ".rb": "Ruby",
    ".php": "PHP",
    ".c": "C",
    ".cpp": "C++",
    ".h": "C/C++",
    ".cs": "C#",
    ".swift": "Swift",
    ".kt": "Kotlin",
    ".md": "Markdown",
    ".json": "JSON",
    ".yml": "YAML",
    ".yaml": "YAML",
    ".toml": "TOML",
    ".sh": "Shell",
    ".html": "HTML",
    ".css": "CSS",
    ".scss": "SCSS",
    ".sql": "SQL",
}

CODE_LANGUAGES = {
    "Python", "JavaScript", "TypeScript", "Go", "Rust", "Java", "Ruby", "PHP",
    "C", "C++", "C/C++", "C#", "Swift", "Kotlin", "Shell", "HTML", "CSS", "SCSS", "SQL"
}


def _gather_facts(root: Path) -> dict[str, Any]:
    """Scan the directory tree for common quality signals."""
    facts: dict[str, Any] = {
        "file_count": 0,
        "languages": set(),
        "has_readme": False,
        "has_license": False,
        "has_tests": False,
        "has_gitignore": False,
        "has_pyproject": False,
        "has_requirements": False,
        "has_src_layout": False,
        "has_ci": False,
        "top_extensions": {},
        "has_contributing": False,
        "has_codeowners": False,
        "has_security": False,
    }

    ext_counts: dict[str, int] = {}
    ignore_dirs = {
        ".git",
        ".venv",
        "venv",
        "__pycache__",
        "node_modules",
        ".mypy_cache",
        "dist",
        "build",
        ".next",
        "target",
    }

    for _dirpath, dirnames, filenames in os.walk(root):
        # Prune ignored dirs
        dirnames[:] = [d for d in dirnames if d not in ignore_dirs]

        for name in filenames:
            facts["file_count"] += 1
            ext = Path(name).suffix.lower()
            if ext:
                ext_counts[ext] = ext_counts.get(ext, 0) + 1

            lower_name = name.lower()
            if lower_name in {"readme.md", "readme.rst", "readme.txt", "readme"}:
                facts["has_readme"] = True
            if lower_name.startswith("license"):
                facts["has_license"] = True
            if lower_name == ".gitignore":
                facts["has_gitignore"] = True
            if lower_name in {"pyproject.toml", "setup.py", "setup.cfg"}:
                facts["has_pyproject"] = True
            if "requirements" in lower_name and lower_name.endswith((".txt", ".in")):
                facts["has_requirements"] = True
            if lower_name in {"contributing.md", "contributing"}:
                facts["has_contributing"] = True
            if lower_name in {"codeowners", ".github/codowners"}:
                # NOTE: "codowners" is a common typo — we still catch it
                facts["has_codeowners"] = True
            if lower_name in {"security.md", "security"}:
                facts["has_security"] = True

        # dir signals
        if "tests" in [d.lower() for d in dirnames] or any("test" in d.lower() for d in dirnames):
            facts["has_tests"] = True
        if (root / "src").exists():
            facts["has_src_layout"] = True
        ci_indicators = [
            (root / ".github" / "workflows"),
            (root / ".circleci"),
            (root / ".gitlab-ci.yml"),
        ]
        if any(p.exists() for p in ci_indicators):
            facts["has_ci"] = True

        # Language detection
        for fname in filenames:
            ext = Path(fname).suffix.lower()
            if ext in LANGUAGE_MAP:
                facts["languages"].add(LANGUAGE_MAP[ext])

    # Sort languages by popularity in the project
    sorted_langs = sorted(
        [(ext, count) for ext, count in ext_counts.items() if ext in LANGUAGE_MAP],
        key=lambda x: -x[1],
    )
    facts["top_extensions"] = {LANGUAGE_MAP[e]: c for e, c in sorted_langs[:5]}

    # Pick top 3 human language names, preferring actual code languages
    all_langs = [LANGUAGE_MAP[e] for e, _ in sorted_langs] if sorted_langs else []
    code_langs = [lang for lang in all_langs if lang in CODE_LANGUAGES]
    facts["languages"] = code_langs[:3] if code_langs else all_langs[:3]

    # Normalize tests detection better (ignore venv + hidden)
    if not facts["has_tests"]:
        ignored_globs = {".*", ".venv", "venv", "node_modules", "__pycache__", "site-packages"}
        for p in root.rglob("*test*.py"):
            if any(part in ignored_globs or part.startswith(".") for part in p.parts):
                continue
            facts["has_tests"] = True
            break
        if not facts["has_tests"]:
            for p in list(root.rglob("test_*.py"))[:5] + list(root.rglob("*_test.py"))[:5]:
                if any(part in ignored_globs or part.startswith(".") for part in p.parts):
                    continue
                facts["has_tests"] = True
                break

    return facts


def _generate_suggestions(analysis: RepoAnalysis, facts: dict[str, Any]) -> list[str]:
    """Produce human-friendly next steps based on analysis."""
    suggestions: list[str] = []

    if not analysis.has_readme:
        suggestions.append("Add a clear README.md with project overview, install, and usage.")

    if not analysis.has_license:
        suggestions.append("Add a LICENSE file (MIT, Apache-2.0, etc.).")

    if not analysis.has_tests:
        suggestions.append("Add a tests/ directory + at least a basic test suite.")

    if not analysis.has_gitignore:
        suggestions.append("Add a .gitignore (use gitignore.io or language templates).")

    if not analysis.has_pyproject and not analysis.has_requirements:
        suggestions.append("Introduce pyproject.toml (or requirements) for reproducible installs.")

    if not facts.get("has_ci"):
        suggestions.append(
            "Add a CI workflow (.github/workflows/ci.yml) — even a simple lint+test is powerful."
        )

    if not facts.get("has_contributing"):
        suggestions.append("Add CONTRIBUTING.md with how to set up dev environment and submit PRs.")

    if analysis.commit_count < 5:
        suggestions.append("Make a few more commits to demonstrate ongoing work / history.")

    if analysis.garden_score < 65:
        suggestions.append("Focus on docs + tests first — they give the biggest score lift.")

    # Language specific
    if "Python" in analysis.languages:
        if not (analysis.path / "pyproject.toml").exists():
            suggestions.append("Use pyproject.toml + uv/poetry for modern Python packaging.")

    if len(suggestions) == 0:
        suggestions.append(
            "Your garden looks healthy! Consider adding architecture diagrams or examples."
        )

    return suggestions[:7]  # keep it actionable, not overwhelming

