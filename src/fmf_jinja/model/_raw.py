# SPDX-FileCopyrightText: 2026 Cristian Le
#
# SPDX-License-Identifier: GPL-3.0-or-later
from typing import Any

import attrs
import cattrs
from cattrs.dispatch import StructureHook
from cattrs.strategies import use_class_methods

from .._wrapper.attrs import ContainerInstance, is_container

__all__ = [
    "raw_converter",
]

raw_converter = cattrs.Converter(
    forbid_extra_keys=True,
)


@raw_converter.register_structure_hook_factory(is_container)
def structure_container[C: type[ContainerInstance]](
    cls: C,
    converter: cattrs.Converter,
) -> StructureHook:
    assert is_container(cls)

    cls_structure = cattrs.gen.make_dict_structure_fn(
        cls,
        converter,
        **{
            attrib.name: cattrs.override(struct_hook=attr_structure)
            for attrib in attrs.fields(cls)
            if (
                attr_structure := structure_field_with_converter(
                    attrib=attrib,
                    converter=converter,
                )
            )
        },
    )

    if cls.__container__.converter is not None:
        dummy_field = attrs.Attribute(
            name=None,
            default=None,
            validator=None,
            repr=None,
            cmp=None,
            hash=None,
            init=None,
            inherited=None,
            type=cls,
        )

        def structure(raw_value: Any, _type: type[C]) -> C:  # noqa: ANN401
            value = cls.__container__.converter(raw_value, None, dummy_field)
            return cls_structure(value, _type)

        return structure

    return cls_structure


def structure_field_with_converter[T](
    attrib: attrs.Attribute[T],
    converter: cattrs.Converter,
) -> StructureHook | None:
    if not attrib.converter:
        return None
    original_structure = converter.get_structure_hook(attrib.type)

    def structure(raw_value: Any, _type: type[T]) -> T:  # noqa: ANN401
        value = attrib.converter(raw_value, None, attrib)
        return original_structure(value, _type)

    return structure


use_class_methods(raw_converter, "_from_raw", "_to_raw")
