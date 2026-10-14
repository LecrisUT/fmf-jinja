# SPDX-FileCopyrightText: 2026 Cristian Le
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""Main `fmf-jinja` module."""

from __future__ import annotations

from ._version import __version__
from .template import TemplateContext

__all__ = [
    "TemplateContext",
    "__version__",
]
