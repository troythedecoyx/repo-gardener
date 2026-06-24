import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import print as rprint
from pathlib import Path
import git
import tempfile
import shutil
from urllib.parse import urlparse
import subprocess
import json

app = typer.Typer(
    help="🌱 RepoGardener — Analyze any Git repo and give it a Garden Score."
)
console = Console()

IGNORE_PATTERNS = {".git", "venv", "env", ".venv", ".env", "__pycache__", "node_modules", "dist", "build", ".pytest_cache", ".ruff_cache", ".mypy_cache"}

def should_ignore(path: Path) -> bool:
    name = path.name.lower()
    return name in IGNORE_PATTERNS or any(p in str(path).lower() for p in IGNORE_PATTERNS)

def clone_repo(url: str) -> Path:
    console.print(f"[yellow]Cloning {url}...[/yellow]")
    temp_dir = Path(tempfile.mkdtemp(prefix="repogardener_"))
    try:
        git.Repo.clone_from(url, temp_dir)
        console.print("[green]✓ Cloned successfully[/green]")
        return temp_dir
    except Exception as e:
        console.print(f"[red]Failed to clone: {e}[/red]")
        raise typer.Exit(1)

def run_ruff_check(path: Path):
    try:
        result = subprocess.run(
            ["ruff", "check", str(path), "--output-format=json", "--quiet"],
            capture_output=True, text=True, timeout=20
        )
        issues = json.loads(result.stdout) if result.stdout.strip() else []
        score = max(40, 100 - len(issues) * 6)
        return {"score": score, "issues": len(issues)}
    except:
        return {"score": 65, "issues": 0}

def get_garden_score(repo_path: str):
    path = Path(repo_path).resolve()
    is_temp = False

    if str(repo_path).startswith(("http", "git@")):
        path = clone_repo(str(repo_path))
        is_temp = True

    try:
        repo = git.Repo(path)
        is_git = True
    except:
        is_git = False
        repo = None

    py_files = [f for f in path.rglob("*.py") if not should_ignore(f)]
    md_files = [f for f in path.rglob("*.md") if not should_ignore(f)]
    test_files = [f for f in py_files if "test" in f.name.lower()]

    has_readme = (path / "README.md").exists()
    has_license = any((path / f).exists() for f in ["LICENSE", "LICENSE.md", "LICENSE.txt"])
    has_gitignore = (path / ".gitignore").exists()
    has_pyproject = (path / "pyproject.toml").exists()
    has_tests_dir = (path / "tests").exists() or (path / "test").exists()

    commits = 0
    last_commit_date = "N/A"
    if is_git and repo:
        try:
            commits = len(list(repo.iter_commits(max_count=300)))
            if commits > 0:
                last_commit_date = repo.head.commit.committed_datetime.strftime("%Y-%m-%d")
        except:
            pass

    ruff_data = run_ruff_check(path)

    # Scoring
    doc_score = min(100, 50 + (30 if has_readme else 0) + (20 if len(md_files) >= 2 else 0))
    test_score = min(100, 40 + (40 if has_tests_dir or len(test_files) > 3 else 0) + (20 if len(test_files) > 8 else 0))
    struct_score = min(100, 60 + (15 if has_gitignore else 0) + (15 if has_pyproject else 0) + (10 if has_license else 0))
    git_score = min(100, 40 + min(commits * 4, 60))
    quality_score = ruff_data["score"]

    overall = int((doc_score + test_score + struct_score + git_score + quality_score) / 5)

    if is_temp:
        shutil.rmtree(path, ignore_errors=True)

    suggestions = []
    if doc_score < 80:
        suggestions.append("→ Add or improve your README.md")
    if test_score < 70:
        suggestions.append("→ Add tests (tests/ folder or *_test.py files)")
    if git_score < 70:
        suggestions.append("→ Make more regular commits")
    if quality_score < 80:
        suggestions.append("→ Run `ruff check --fix` to improve code quality")

    return {
        "overall": overall,
        "details": {
            "Documentation": {"score": doc_score, "status": "✅ Excellent" if doc_score >= 85 else "🟡 Fair"},
            "Testing & Quality": {"score": test_score, "status": "✅ Good" if test_score >= 70 else "⚠️ Needs work"},
            "Project Structure": {"score": struct_score, "status": "✅ Solid"},
            "Git Hygiene": {"score": git_score, "status": "✅ Active" if commits > 15 else "🟡 Quiet"},
            "Code Quality": {"score": quality_score, "status": f"{'✅' if quality_score >= 80 else '🟡'} ({ruff_data['issues']} issues)"},
        },
        "suggestions": suggestions,
        "stats": {
            "python_files": len(py_files),
            "test_files": len(test_files),
            "commits": commits,
            "last_updated": last_commit_date,
        }
    }

@app.command()
def analyze(repo_path: str = typer.Argument(".", help="Local path or GitHub URL")):
    """Analyze a repository and show its Garden Score."""
    console.print(Panel.fit(f"[bold green]🌱 Analyzing:[/] {repo_path}"))
    
    data = get_garden_score(repo_path)
    
    table = Table(title="🌿 Garden Score Breakdown")
    table.add_column("Category", style="cyan")
    table.add_column("Score", style="magenta")
    table.add_column("Status", style="green")
    
    for cat, info in data["details"].items():
        table.add_row(cat, f"{info['score']}/100", info["status"])
    
    console.print(table)
    rprint(f"\n[bold]Overall Garden Score:[/] [bold yellow]{data['overall']}/100[/] 🌱\n")
    
    if data["suggestions"]:
        rprint("[yellow]💡 Suggestions to improve:[/]")
        for s in data["suggestions"]:
            rprint(f"   {s}")

# Aliases
@app.command(name="scan")
def scan_alias(repo_path: str = typer.Argument(".", help="Local path or GitHub URL")):
    analyze(repo_path)

if __name__ == "__main__":
    app()
