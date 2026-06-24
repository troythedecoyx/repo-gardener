"""Scoring engine for Garden Score.

Dimensions (current):
- Documentation
- Testing & Quality
- Project Structure
- Git Hygiene & Maintenance
- Dependencies & Config
- Security / Best Practices (lightweight)
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import git

    from .analyzer import RepoAnalysis


@dataclass
class DimensionScore:
    name: str
    score: int  # 0-100
    weight: float = 1.0
    notes: str | None = None


def compute_dimensions(
    analysis: RepoAnalysis,
    facts: dict[str, Any],
    *,
    repo: git.Repo | None = None,
) -> list[DimensionScore]:
    """Return list of scored dimensions."""
    dims: list[DimensionScore] = []

    # 1. Documentation (weight 1.5)
    doc_score = 0
    notes = []
    if analysis.has_readme:
        doc_score += 45
        notes.append("README present")
    else:
        notes.append("Missing README")

    if facts.get("has_contributing"):
        doc_score += 20
        notes.append("CONTRIBUTING guide")
    else:
        notes.append("No CONTRIBUTING.md")

    if analysis.has_license:
        doc_score += 25
        notes.append("LICENSE file")
    else:
        notes.append("Missing LICENSE")

    if facts.get("has_codeowners"):
        doc_score += 10

    doc_score = min(100, doc_score)
    dims.append(DimensionScore("Documentation", doc_score, weight=1.5, notes="; ".join(notes)))

    # 2. Testing & Quality (weight 1.3)
    test_score = 0
    tnotes = []
    if analysis.has_tests:
        test_score += 55
        tnotes.append("Test directory/files found")
    else:
        tnotes.append("No obvious test files")

    if analysis.has_pyproject or analysis.has_requirements:
        test_score += 20
        tnotes.append("Dependency manifest present")

    # Very rough: look for common quality files
    if (analysis.path / ".pre-commit-config.yaml").exists() or (
        analysis.path / "ruff.toml"
    ).exists():
        test_score += 15
        tnotes.append("Linting / pre-commit config")

    if facts.get("has_ci"):
        test_score += 10
        tnotes.append("CI config detected")

    test_score = min(100, test_score)
    dims.append(
        DimensionScore("Testing & Quality", test_score, weight=1.3, notes="; ".join(tnotes))
    )

    # 3. Project Structure (weight 1.0)
    struct_score = 30  # base
    snotes = []
    if facts.get("has_src_layout"):
        struct_score += 25
        snotes.append("src/ layout")
    if analysis.has_gitignore:
        struct_score += 15
        snotes.append(".gitignore")
    if analysis.has_pyproject:
        struct_score += 20
        snotes.append("Modern Python packaging")
    elif analysis.has_requirements:
        struct_score += 10

    if len(analysis.languages) >= 1:
        struct_score += 10

    struct_score = min(100, struct_score)
    dims.append(
        DimensionScore(
            "Project Structure", struct_score, weight=1.0, notes="; ".join(snotes) or "Basic layout"
        )
    )

    # 4. Git Hygiene (weight 1.0)
    git_score = 20
    gnotes = []
    if repo is not None:
        try:
            if not repo.is_dirty():
                git_score += 15
                gnotes.append("Working tree clean")
            # Count branches
            branches = list(repo.branches)
            if len(branches) > 1:
                git_score += 10
            gnotes.append(f"{len(branches)} branch(es)")

            # Recent activity rough (use commit count as proxy)
            if analysis.commit_count > 20:
                git_score += 20
            elif analysis.commit_count > 5:
                git_score += 12

            if repo.head.is_detached:
                gnotes.append("Detached HEAD (consider branch)")
        except Exception:
            pass
    else:
        gnotes.append("Not a git repo (or shallow)")

    if analysis.has_gitignore:
        git_score += 15
        gnotes.append("gitignore present")

    git_score = min(100, git_score)
    dims.append(DimensionScore("Git Hygiene", git_score, weight=1.0, notes="; ".join(gnotes)))

    # 5. Dependencies & Config (weight 0.8)
    dep_score = 25
    dnotes = []
    if analysis.has_pyproject:
        dep_score += 50
        dnotes.append("pyproject.toml")
    if analysis.has_requirements:
        dep_score += 25
        dnotes.append("requirements present")

    # Detect lockfiles
    lockfiles = ["poetry.lock", "uv.lock", "Pipfile.lock"]
    if any((analysis.path / lf).exists() for lf in lockfiles):
        dep_score += 15
        dnotes.append("Lockfile present")

    dep_score = min(100, dep_score)
    dims.append(
        DimensionScore("Dependencies & Config", dep_score, weight=0.8, notes="; ".join(dnotes))
    )

    # 6. Security & Polish (light) (weight 0.9)
    sec_score = 40
    sec_notes = []
    if facts.get("has_security"):
        sec_score += 25
        sec_notes.append("SECURITY.md present")
    # Very naive secret scan for common patterns in files (limited)
    secret_hints = _quick_secret_check(analysis.path)
    if secret_hints:
        sec_score = max(10, sec_score - 30)
        sec_notes.append(f"Potential secrets found: {', '.join(secret_hints[:2])}")
    else:
        sec_score += 20
        sec_notes.append("No obvious secrets in top-level files")

    if analysis.has_license:
        sec_score += 15

    sec_score = min(100, sec_score)
    dims.append(
        DimensionScore("Security & Polish", sec_score, weight=0.9, notes="; ".join(sec_notes))
    )

    return dims


def _quick_secret_check(root: Path) -> list[str]:
    """Extremely lightweight secret detection on a few files. Not a real scanner."""
    hints: list[str] = []
    suspicious = [
        "aws_secret",
        "apikey",
        "api_key",
        "secret_key",
        "password=",
        "ghp_",
        "sk-",
        "-----BEGIN",
    ]
    candidates = [".env", ".env.example", "config.py", "settings.py", "secrets.py"]

    for name in candidates:
        p = root / name
        if p.is_file():
            try:
                text = p.read_text(errors="ignore").lower()
                for s in suspicious:
                    if s.lower() in text:
                        hints.append(name)
                        break
            except Exception:
                pass
    return hints
