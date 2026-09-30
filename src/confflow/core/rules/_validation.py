from __future__ import annotations

from typing import TYPE_CHECKING

from ..entries.base import Entry
from ..exceptions import SchemaError

if TYPE_CHECKING:
    from collections.abc import Collection, Sequence

_MINIMUM_GROUP_SIZE = 2


def _validate_group_members(members: Sequence[Entry]) -> tuple[Entry, ...]:
    member_tuple = tuple(members)
    if len(member_tuple) < _MINIMUM_GROUP_SIZE:
        raise SchemaError("rule requires at least two members")
    if any(not isinstance(member, Entry) for member in member_tuple):
        raise SchemaError("rule members must be Entry instances")
    if len(set(member_tuple)) != len(member_tuple):
        raise SchemaError("rule cannot reference the same member more than once")
    return member_tuple


def _validate_pair(source: Entry, target: Entry) -> None:
    if not isinstance(source, Entry) or not isinstance(target, Entry):
        raise SchemaError("rule source and target must be Entry instances")
    if source is target:
        raise SchemaError("rule source and target must be different members")


def _validate_directional_group(
    source: Entry, targets: Sequence[Entry]
) -> tuple[Entry, ...]:
    if not isinstance(source, Entry):
        raise SchemaError("rule source must be an Entry")
    target_tuple = tuple(targets)
    if len(target_tuple) < _MINIMUM_GROUP_SIZE:
        raise SchemaError("rule requires at least two target members")
    if any(not isinstance(target, Entry) for target in target_tuple):
        raise SchemaError("rule targets must be Entry instances")
    if len(set(target_tuple)) != len(target_tuple):
        raise SchemaError("rule cannot reference the same target more than once")
    if source in target_tuple:
        raise SchemaError("rule source cannot also be a target")
    return target_tuple


def _present_count(members: Sequence[Entry], present_members: Collection[Entry]) -> int:
    return sum(member in present_members for member in members)
