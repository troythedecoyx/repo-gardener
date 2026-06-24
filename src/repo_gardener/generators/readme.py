"""README generator using Jinja2 + analysis data.

This is the beginning of the "beautiful auto-generated professional README" feature.
"""

from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from ..analyzer import RepoAnalysis

# A solid default template inline for portability (can be moved to templates/ later)
README_TEMPLATE = """# {{ project_name }}

{{ tagline or "A great project." }}

{% if garden_score is defined %}
> **Garden Score:** {{ garden_score }}/100
{% endif %}

## Overview

{{ overview or "Add a compelling 2-3 sentence description here." }}

## ✨ Features

{% for feat in features %}
- {{ feat }}
{% else %}
- (Add your killer features here)
{% endfor %}

## 🚀 Getting Started

### Installation

```bash
# TODO: fill in real instructions
pip install -e .
# or uv sync
```

### Usage

```python
# TODO: example usage
```

## 🧪 Testing

Run the test suite:

```bash
pytest
```

## 🤝 Contributing

We love contributions!

1. Fork the repo
2. Create your feature branch
3. Submit a PR

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## 📄 License

{{ license or "MIT" }}

---

*This README was lovingly tended by [RepoGardener](https://github.com/yourname/repo-gardener).*
"""

def generate_readme(
    analysis: RepoAnalysis,
    *,
    output_path: Path | None = None,
    project_name: str | None = None,
    tagline: str | None = None,
    overview: str | None = None,
) -> str:
    """Generate a polished README.md string from analysis data."""
    env = Environment(
        loader=FileSystemLoader(searchpath="."),
        autoescape=select_autoescape(),
        trim_blocks=True,
        lstrip_blocks=True,
    )

    # Use inline template for now
    template = env.from_string(README_TEMPLATE)

    context = {
        "project_name": project_name or analysis.repo_name or "My Project",
        "tagline": tagline,
        "garden_score": analysis.garden_score,
        "overview": overview,
        "features": [
            "Well structured & scored by RepoGardener",
            "Great docs (or working on it)",
            "Tests & CI where applicable",
        ],
        "license": "MIT" if analysis.has_license else "Add your license here",
    }

    rendered = template.render(**context)

    if output_path:
        output_path = Path(output_path)
        output_path.write_text(rendered)
    return rendered
