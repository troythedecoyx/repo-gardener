# 🌱 RepoGardener

**Analyze any Git repository — get a beautiful "Garden Score" in seconds.**

A modern, developer-friendly CLI tool that evaluates repositories on documentation, testing, structure, Git hygiene, and code quality.

## ✨ Features

- Analyze **local folders** or **any public GitHub URL** (auto-clones + cleans up)
- Comprehensive **Garden Score** (0–100) with detailed breakdown
- Real code quality analysis via Ruff
- Smart improvement suggestions
- Beautiful terminal output with Rich

## 🚀 Installation

```bash
pip install git+https://github.com/troythedecoyx/repo-gardener.git
```

## 📖 Usage

```bash
# Analyze current directory
repo-gardener scan .

# Analyze any GitHub repository
repo-gardener analyze https://github.com/pallets/flask
```

## Example Output

```
🌱 Analyzing: https://github.com/pallets/flask
Overall Garden Score: 100/100 🌱

Documentation       100/100  ✅ Excellent
Testing & Quality   100/100  ✅ Good
Project Structure   100/100  ✅ Solid
Git Hygiene         100/100  ✅ Active
Code Quality        100/100  ✅ (0 issues)
```

💡 Suggestions to improve:
   → (only shows when needed)

## Why I Built It

Most GitHub repositories are hard to evaluate quickly. Recruiters, contributors, and developers waste time digging through poor structure and missing documentation.

RepoGardener gives you an instant, objective health check — like a gardener tending to your codebase.

## Contributing

Feel free to open issues or PRs!

---

Made with ❤️ by Troy Scalf
