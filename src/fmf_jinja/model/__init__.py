# SPDX-FileCopyrightText: 2026 Cristian Le
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Data model of the inputs."""

from . import template
from ._raw import raw_converter
from .template import File, Template

__all__ = [
    "File",
    "Template",
    "raw_converter",
    "template",
]
