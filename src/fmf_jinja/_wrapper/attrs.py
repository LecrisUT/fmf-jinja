# SPDX-FileCopyrightText: 2026 Cristian Le
#
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from typing import (
    Any,
    ClassVar,
    Protocol,
    Self,
    TypeGuard,
    dataclass_transform,
    overload,
)

import attrs

TYPE_CHECKING = False
if TYPE_CHECKING:
    from collections.abc import Callable, Mapping

    from attrs import (
        _ConverterType,
        _EqOrderType,
        _FieldTransformer,
        _OnSetAttrArgType,
        _ReprArgType,
        _ValidatorArgType,
    )


@overload
def field(
    *,
    default: None = ...,
    validator: None = ...,
    repr: _ReprArgType = ...,
    hash: bool | None = ...,
    init: bool = ...,
    metadata: Mapping[Any, Any] | None = ...,
    converter: None = ...,
    factory: None = ...,
    kw_only: bool | None = ...,
    eq: bool | None = ...,
    order: bool | None = ...,
    on_setattr: _OnSetAttrArgType | None = ...,
    alias: str | None = ...,
    type: type | None = ...,
) -> Any: ...  # noqa: ANN401


@overload
def field[T](
    *,
    default: None = ...,
    validator: _ValidatorArgType[T] | None = ...,
    repr: _ReprArgType = ...,
    hash: bool | None = ...,
    init: bool = ...,
    metadata: Mapping[Any, Any] | None = ...,
    converter: _ConverterType
    | list[_ConverterType]
    | tuple[_ConverterType, ...]
    | None = ...,
    factory: Callable[[], T] | None = ...,
    kw_only: bool | None = ...,
    eq: _EqOrderType | None = ...,
    order: _EqOrderType | None = ...,
    on_setattr: _OnSetAttrArgType | None = ...,
    alias: str | None = ...,
    type: type | None = ...,
) -> T: ...


@overload
def field[T](
    *,
    default: T,
    validator: _ValidatorArgType[T] | None = ...,
    repr: _ReprArgType = ...,
    hash: bool | None = ...,
    init: bool = ...,
    metadata: Mapping[Any, Any] | None = ...,
    converter: _ConverterType
    | list[_ConverterType]
    | tuple[_ConverterType, ...]
    | None = ...,
    factory: Callable[[], T] | None = ...,
    kw_only: bool | None = ...,
    eq: _EqOrderType | None = ...,
    order: _EqOrderType | None = ...,
    on_setattr: _OnSetAttrArgType | None = ...,
    alias: str | None = ...,
    type: type | None = ...,
) -> T: ...


# This form covers type=non-Type: e.g. forward references (str), Any
@overload
def field[T](
    *,
    default: T | None = ...,
    validator: _ValidatorArgType[T] | None = ...,
    repr: _ReprArgType = ...,
    hash: bool | None = ...,
    init: bool = ...,
    metadata: Mapping[Any, Any] | None = ...,
    converter: _ConverterType
    | list[_ConverterType]
    | tuple[_ConverterType, ...]
    | None = ...,
    factory: Callable[[], T] | None = ...,
    kw_only: bool | None = ...,
    eq: _EqOrderType | None = ...,
    order: _EqOrderType | None = ...,
    on_setattr: _OnSetAttrArgType | None = ...,
    alias: str | None = ...,
    type: type | None = ...,
) -> Any: ...  # noqa: ANN401


def field(**kwargs):
    return attrs.field(**kwargs)


@overload
@dataclass_transform(field_specifiers=(field,))
def container[C: type](
    maybe_cls: C,
    *,
    these: dict[str, Any] | None = ...,
    repr: bool = ...,
    unsafe_hash: bool | None = ...,
    hash: bool | None = ...,
    init: bool = ...,
    slots: bool = ...,
    frozen: bool = ...,
    weakref_slot: bool = ...,
    str: bool = ...,
    auto_attribs: bool = ...,
    kw_only: bool = ...,
    cache_hash: bool = ...,
    auto_exc: bool = ...,
    eq: bool | None = ...,
    order: bool | None = ...,
    auto_detect: bool = ...,
    getstate_setstate: bool | None = ...,
    on_setattr: _OnSetAttrArgType | None = ...,
    field_transformer: _FieldTransformer | None = ...,
    match_args: bool = ...,
    converter: attrs.Converter[Any, Any] | None = ...,
) -> C: ...


@overload
@dataclass_transform(field_specifiers=(field,))
def container[C: type](
    maybe_cls: None = ...,
    *,
    these: dict[str, Any] | None = ...,
    repr: bool = ...,
    unsafe_hash: bool | None = ...,
    hash: bool | None = ...,
    init: bool = ...,
    slots: bool = ...,
    frozen: bool = ...,
    weakref_slot: bool = ...,
    str: bool = ...,
    auto_attribs: bool = ...,
    kw_only: bool = ...,
    cache_hash: bool = ...,
    auto_exc: bool = ...,
    eq: bool | None = ...,
    order: bool | None = ...,
    auto_detect: bool = ...,
    getstate_setstate: bool | None = ...,
    on_setattr: _OnSetAttrArgType | None = ...,
    field_transformer: _FieldTransformer | None = ...,
    match_args: bool = ...,
    converter: attrs.Converter[Any, Any] | None = ...,
) -> Callable[[C], C]: ...


def container[C: type](maybe_cls: C | None = None, *, converter=None, **kwargs):
    def wrap(cls: C) -> C:
        cls = attrs.define(cls, **kwargs)
        cls.__container__ = ContainerClassMetadata(converter=converter)
        return cls

    if maybe_cls is None:
        return wrap
    return wrap(maybe_cls)


@attrs.define
class ContainerClassMetadata[C: type]:
    converter: attrs.Converter[Any, C] | None


class ContainerInstance(attrs.AttrsInstance, Protocol):
    __container__: ClassVar[ContainerClassMetadata[type[Self]]]


def is_container(cls: type[Any]) -> TypeGuard[type[ContainerInstance]]:
    return bool(attrs.has(cls)) and hasattr(cls, "__container__")
