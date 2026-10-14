# SPDX-FileCopyrightText: 2026 Cristian Le
#
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from typing import Any, overload

import attrs

__all__ = [
    "ensure_dict_from_field",
    "ensure_list",
]


@overload
def _ensure_list[T](value: list[T]) -> list[T]: ...


@overload
def _ensure_list[T](value: T) -> list[T]: ...


def _ensure_list(value):
    """
    Make sure the field is normalized to a list.
    """
    if not isinstance(value, list):
        value = [value]
    return value


ensure_list = attrs.Converter(
    _ensure_list,
)


def ensure_dict_from_field(
    field: str,
) -> attrs.Converter[str | dict[str, Any], dict[str, Any]]:
    """
    Make sure the field is normalized to a string to a dict.
    """

    def _converter(value: str | dict[str, Any]) -> dict[str, Any]:
        if isinstance(value, str):
            return {field: value}
        if isinstance(value, dict):
            return value
        msg = "Only str and dict inputs are supported"
        raise TypeError(msg)

    return attrs.Converter(_converter)
