# 🌱 RepoGardener

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![GitHub](https://img.shields.io/badge/github-troythedecoyx/repo--gardener-181717?logo=github)](https://github.com/troythedecoyx/repo-gardener)

**Analyze any Git repository — local or from GitHub — and get a beautiful "Garden Score" in seconds.**

RepoGardener is a delightful CLI tool that evaluates your codebases like a gardener tending plants. It gives each repo a 0–100 Garden Score across Documentation, Testing & Quality, Project Structure, Git Hygiene, and Code Quality (powered by Ruff).

Use it locally, in CI, or to quickly assess any public GitHub project.

## 🚀 Try it now

```bash
repo-gardener analyze https://github.com/troythedecoyx/repo-gardener
```

(Shows a 92/100 Garden Score — perfect Documentation, excellent Code Quality.)

## ✨ Features

- 🌿 Analyze **local paths** or **any public GitHub URL** (auto-clones + cleans up temp files)
- 📊 Rich **Garden Score** (0–100) with visual breakdown and status
- 🧹 Built-in Ruff code quality checks
- 💡 Smart, actionable improvement suggestions
- 📤 `--json` output for scripts and CI
- 🌱 `suggest` command for detailed improvement plans
- 🏷️ `badge` command for auto-generated health badges/cards
- 🌐 Basic support for multiple languages/ecosystems (Python, JS/TS, Go, Rust, etc.)
- 🎨 Beautiful Rich-powered terminal UI

## 🚀 Installation

```bash
# Install directly from Git (current method)
pip install git+https://github.com/troythedecoyx/repo-gardener.git

# Coming soon to PyPI:
# pip install repo-gardener
```

For development:

```bash
git clone https://github.com/troythedecoyx/repo-gardener.git
cd repo-gardener
pip install -e .
```

## 📖 Usage

```bash
# Analyze current directory
repo-gardener scan .

# Analyze specific path
repo-gardener analyze /path/to/project

# Analyze any GitHub repo
repo-gardener analyze https://github.com/troythedecoyx/repo-gardener

# JSON output (great for CI/scripts)
repo-gardener analyze . --json

# Get detailed suggestions
repo-gardener suggest https://github.com/pallets/flask
```

## Demo

```bash
$ repo-gardener analyze https://github.com/troythedecoyx/repo-gardener
🌱 Analyzing: https://github.com/troythedecoyx/repo-gardener

Overall Garden Score: 92/100 🌱

Documentation     100/100  ✅ Excellent
Testing & Quality  80/100  ✅ Good
Project Structure 100/100  ✅ Solid
Git Hygiene        80/100  ✅ Active
Code Quality      100/100  ✅ (0 issues)
```

## Why Use This?

- **Quick health checks**: Instantly understand a repo's strengths and gaps.
- **Actionable advice**: Not just numbers — real suggestions you can act on.
- **Great for interviews & reviews**: Show you care about code quality and project hygiene.
- **CI friendly**: Use `--json` to fail builds on low scores or integrate into dashboards.
- **Fun & visual**: The garden theme and rich output make it enjoyable to use.

## 🛠 Development

```bash
pip install -e .
ruff check --fix .
repo-gardener scan .
```

## 🗺️ Roadmap

### ✅ Completed
- Smart Garden Score analysis for local and GitHub repositories
- `--json` output mode for scripting and CI
- `suggest` command with detailed, actionable improvement recommendations
- Real code quality analysis powered by Ruff
- Beautiful terminal UI with Rich
- Automatic temporary cloning + cleanup for remote repos
- Proper versioning and help text
- Full documentation, LICENSE, and CONTRIBUTING.md

The project is now stable and ready for use. Future ideas may be added later based on feedback.

## 🤝 Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

Made with ❤️ by troythedecoyx
