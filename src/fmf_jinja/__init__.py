"""Main `fmf-jinja` module."""

from __future__ import annotations

from ._version import __version__
from .cli import main
from .template import generate

__all__ = [
    "__version__",
    "main",
    "generate",
]
