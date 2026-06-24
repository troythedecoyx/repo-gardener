# 🌱 RepoGardener

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![GitHub](https://img.shields.io/badge/github-troythedecoyx/repo--gardener-181717?logo=github)](https://github.com/troythedecoyx/repo-gardener)

**Analyze any Git repository — local or GitHub URL — and get a beautiful "Garden Score" in seconds.**

RepoGardener is a fun yet practical CLI tool that tends to your codebases like a garden. It scores repos across Documentation, Testing & Quality, Project Structure, Git Hygiene, and Code Quality (powered by Ruff).

Perfect for developers, recruiters, open-source maintainers, and anyone who wants quick, actionable insights into repo health.

## ✨ Features

- 🔍 Analyze **local directories** or **any public GitHub URL** (auto-clones, analyzes, and cleans up)
- 📊 **Garden Score** (0–100) with rich visual breakdown
- 🧹 Real-time code quality analysis via [Ruff](https://github.com/astral-sh/ruff)
- 💡 Smart, actionable improvement suggestions
- 🎨 Beautiful terminal UI with Rich (tables, panels, emojis)
- ⚡ Fast and lightweight

## 🚀 Installation

```bash
# From Git (recommended for now)
pip install git+https://github.com/troythedecoyx/repo-gardener.git

# Or clone and install editable
git clone https://github.com/troythedecoyx/repo-gardener.git
cd repo-gardener
pip install -e .
```

## 📖 Usage

```bash
# Analyze the current directory
repo-gardener scan .

# Analyze a specific local path
repo-gardener analyze /path/to/my-project

# Analyze any public GitHub repository (magic!)
repo-gardener analyze https://github.com/pallets/flask
repo-gardener analyze https://github.com/troythedecoyx/repo-gardener
```

## Example Output

```
🌱 Analyzing: https://github.com/troythedecoyx/repo-gardener
Overall Garden Score: 89/100 🌱

Documentation       100/100  ✅ Excellent
Testing & Quality    80/100  ✅ Good
Project Structure   100/100  ✅ Solid
Git Hygiene          80/100  ✅ Active
Code Quality        100/100  ✅ (0 issues)

💡 Suggestions to improve:
   → (only shows when needed)
```

## 🛠 Development

```bash
git clone https://github.com/troythedecoyx/repo-gardener.git
cd repo-gardener
pip install -e .
ruff check .
repo-gardener scan .
```

## 🗺️ Roadmap

- [ ] `suggest` command for detailed improvement plans
- [ ] JSON output mode (`--json`)
- [ ] Support for more languages/ecosystems
- [ ] Auto-generated health badges/cards
- [ ] GitHub Action for CI
- [ ] Even smarter suggestions

## 🤝 Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md).

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

Made with ❤️ by troythedecoyx
