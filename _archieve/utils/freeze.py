from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING, cast

from ..core.entries.array import Array
from ..core.entries.mapping import Mapping
from ..core.entries.scalars.base import Scalar
from ..core.entries.table import Table

if TYPE_CHECKING:
    from collections.abc import Mapping as MappingValue, Sequence

    from ..core.entries.base import Entry
    from ..types import ConfigurationValue, _ConfigurationScalar


def freeze_configuration(
    entries: tuple[Entry, ...], data: MappingValue[str, object]
) -> MappingValue[str, ConfigurationValue]:
    frozen: dict[str, ConfigurationValue] = {}
    for member in entries:
        if member.name not in data:
            continue
        frozen[member.name] = _freeze_member(member, data[member.name])
    return MappingProxyType(frozen)


def _freeze_member(member: Entry, value: object) -> ConfigurationValue:
    if isinstance(member, Scalar):
        return cast("_ConfigurationScalar", value)
    if isinstance(member, Table):
        return freeze_configuration(
            member.entries, cast("MappingValue[str, object]", value)
        )
    if isinstance(member, Array):
        return _freeze_array(member, value)
    if isinstance(member, Mapping):
        return _freeze_map(member, value)
    raise TypeError(f"unsupported member type: {type(member).__name__}")


def _freeze_array(member: Array, value: object) -> ConfigurationValue:
    items = cast("Sequence[object]", value)
    element = member.element
    if element is not None:
        scalar_items = tuple(cast("_ConfigurationScalar", item) for item in items)
        if member.unique:
            return frozenset(scalar_items)
        return scalar_items

    entries = member.entries or ()
    return tuple(
        freeze_configuration(entries, cast("MappingValue[str, object]", item))
        for item in items
    )


def _freeze_map(
    member: Mapping, value: object
) -> MappingValue[str, ConfigurationValue]:
    mapping = cast("MappingValue[str, object]", value)
    target = member.value
    frozen: dict[str, ConfigurationValue] = {}
    for key, mapped_value in mapping.items():
        if target is not None:
            frozen[key] = cast("_ConfigurationScalar", mapped_value)
        else:
            frozen[key] = freeze_configuration(
                member.entries or (),
                cast("MappingValue[str, object]", mapped_value),
            )
    return MappingProxyType(frozen)
