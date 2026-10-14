# SPDX-FileCopyrightText: 2026 Cristian Le
#
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from io import StringIO
from typing import Any

import cattrs
from cattrs.strategies import use_class_methods
from ruamel.yaml import YAML

from ._raw import raw_converter

TYPE_CHECKING = False
if TYPE_CHECKING:
    from pathlib import Path

    from cattrs.dispatch import StructureHook, UnstructureHook


__all__ = [
    "yaml_converter",
]


class YamlConverter(cattrs.Converter):
    _yaml: YAML

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # noqa: ANN401
        super().__init__(*args, **kwargs)
        self._yaml = YAML(typ="safe")

    def load[T](self, data: Path | str, cl: type[T]) -> T:
        raw_data = self._yaml.load(data)
        return self.structure(raw_data, cl)

    def dump(
        self,
        obj: Any,  # noqa: ANN401
        unstructure_as: Any = None,  # noqa: ANN401
        stream: Any = None,  # noqa: ANN401
    ) -> str | None:
        return_str = False
        if stream is None:
            stream = StringIO()
            return_str = True
        self._yaml.dump(
            data=self.unstructure(obj, unstructure_as=unstructure_as),
            stream=stream,
        )
        if not return_str:
            return None
        return stream.getvalue()


def _fallback_structure(_type: type) -> StructureHook:
    return raw_converter.get_structure_hook(_type)


def _fallback_unstructure(_type: type) -> UnstructureHook:
    return raw_converter.get_unstructure_hook(_type)


yaml_converter = YamlConverter(
    forbid_extra_keys=True,
    # TODO: This does not really work as expected:
    # issue: https://github.com/python-attrs/cattrs/issues/793
    # expectation: https://catt.rs/en/latest/indepth.html#fallback-hook-factories
    structure_fallback_factory=_fallback_structure,
    unstructure_fallback_factory=_fallback_unstructure,
)
use_class_methods(yaml_converter, "_from_yaml", "_to_yaml")
