"""RepoGardener - An intelligent CLI for tending Git repositories."""

__version__ = "0.1.0"

from .cli import app


def main() -> None:
    """Entry point for the CLI."""
    app()

