"""Basic smoke tests for the analyzer."""

from pathlib import Path


from repo_gardener.analyzer import analyze_repository


def test_analyze_current_project():
    """Analyze this project itself — should succeed and produce a score."""
    result = analyze_repository(Path("."))
    assert result.garden_score >= 0
    assert result.garden_score <= 100
    assert len(result.dimensions) >= 5
    assert isinstance(result.suggestions, list)
    # We have src layout and pyproject, README, etc.
    assert result.has_readme is True
    assert result.has_pyproject is True


def test_json_roundtrip():
    """Ensure dataclasses are serializable (used by --json)."""
    from dataclasses import asdict
    import json

    result = analyze_repository(Path("."))
    data = asdict(result)
    serialized = json.dumps(data, default=str)
    assert "garden_score" in serialized
