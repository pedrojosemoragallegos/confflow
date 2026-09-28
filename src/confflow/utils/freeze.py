from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING, cast

from ..core.definitions.base import Definition
from ..core.members.array import Array
from ..core.members.field import Field
from ..core.members.map import Map
from ..core.members.section import Section

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

    from ..core.members.base import Entry
    from ..core.schema import Schema
    from ..types import ConfigurationValue, _ConfigurationScalar


def freeze_configuration(
    schema: Schema, data: Mapping[str, object]
) -> Mapping[str, ConfigurationValue]:
    frozen: dict[str, ConfigurationValue] = {}
    for member in schema.members:
        if member.name not in data:
            continue
        frozen[member.name] = _freeze_member(member, data[member.name])
    return MappingProxyType(frozen)


def _freeze_member(member: Entry, value: object) -> ConfigurationValue:
    if isinstance(member, Field):
        return cast("_ConfigurationScalar", value)
    if isinstance(member, Section):
        return freeze_configuration(member.schema, cast("Mapping[str, object]", value))
    if isinstance(member, Array):
        return _freeze_array(member, value)
    if isinstance(member, Map):
        return _freeze_map(member, value)
    raise TypeError(f"unsupported member type: {type(member).__name__}")


def _freeze_array(member: Array, value: object) -> ConfigurationValue:
    items = cast("Sequence[object]", value)
    element = member.element
    if isinstance(element, Definition):
        scalar_items = tuple(cast("_ConfigurationScalar", item) for item in items)
        if member.unique:
            return frozenset(scalar_items)
        return scalar_items

    return tuple(
        freeze_configuration(element, cast("Mapping[str, object]", item))
        for item in items
    )


def _freeze_map(member: Map, value: object) -> Mapping[str, ConfigurationValue]:
    mapping = cast("Mapping[str, object]", value)
    target = member.value
    frozen: dict[str, ConfigurationValue] = {}
    for key, mapped_value in mapping.items():
        if isinstance(target, Definition):
            frozen[key] = cast("_ConfigurationScalar", mapped_value)
        else:
            frozen[key] = freeze_configuration(
                target, cast("Mapping[str, object]", mapped_value)
            )
    return MappingProxyType(frozen)
