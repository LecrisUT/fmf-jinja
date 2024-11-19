"""Main `fmf-jinja` module."""

from __future__ import annotations

from ._version import __version__
from .template import TemplateContext

__all__ = [
    "__version__",
    "TemplateContext",
]
