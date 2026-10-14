# SPDX-FileCopyrightText: 2026 Cristian Le
#
# SPDX-License-Identifier: GPL-3.0-or-later
"""Template data model."""

from pathlib import Path
from typing import Any, Self

import cattrs

from .._wrapper.attrs import container, field
from ._base import ensure_dict_from_field, ensure_list
from ._raw import structure_container


@container(converter=ensure_dict_from_field("path"))
class Template:
    """
    Template instructions.
    """

    path: Path
    """Path to the templated file/folder."""
    exclude: list[Path] = field(factory=list)
    """Paths to exclude from being copied or rendered."""


@container
class File:
    """
    Fmf file representation.
    """

    templates: list[Template] = field(factory=list, converter=ensure_list)
    """Templates to generate."""
    vars: dict[str, Any] = field(factory=dict)
    """Jinja variables used in the template files."""
    copy: dict[Path, Path] = field(factory=dict)
    """Files or folders to be copied."""
    links: dict[Path, Path] = field(factory=dict)
    """Symbolic links to be created."""
    output: Path | None = None
    """Output path where to generate the templates."""

    @classmethod
    def _from_raw(cls, data: Any, converter: cattrs.Converter) -> Self:  # noqa: ANN401
        if not isinstance(data, dict):
            msg = f"Invalid input type: {type(data)}"
            raise TypeError(msg)
        if "templates" not in data:
            data["templates"] = "."
        if "vars" not in data:
            vars = data.copy()  # noqa: A001
            del vars["templates"]
            data = {"templates": data["templates"]}
            data["vars"] = vars
        # TODO: Need to get the next preferred structure hook but that is not supported
        #  https://github.com/python-attrs/cattrs/issues/794
        original_structure = structure_container(cls, converter)
        return original_structure(data, cls)
