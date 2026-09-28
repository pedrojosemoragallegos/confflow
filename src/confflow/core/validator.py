from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING, TypeGuard, cast

from .definitions.base import Definition
from .exceptions import InvalidValueError, ValidationError
from .members.array import Array
from .members.field import Field
from .members.map import Map
from .members.section import Section
from .schema import Schema

if TYPE_CHECKING:
    from .members.base import Entry


def validate(schema: Schema, data: object) -> None:
    if not isinstance(schema, Schema):
        raise TypeError("schema must be a Schema")
    _validate_schema(schema, data, ())


def _validate_schema(schema: Schema, data: object, path: tuple[str | int, ...]) -> None:
    if not isinstance(data, Mapping):
        raise InvalidValueError("expected a mapping", path)

    mapping = cast("Mapping[object, object]", data)
    _validate_known_keys(schema, mapping, path)
    present_members = _validate_present_members(schema, mapping, path)

    for rule in schema.rules:
        rule.validate(present_members, path)


def _validate_known_keys(
    schema: Schema, mapping: Mapping[object, object], path: tuple[str | int, ...]
) -> None:
    member_names = {member.name for member in schema.members}
    for key in mapping:
        if type(key) is not str:
            raise ValidationError("member keys must be strings", path)
        if key not in member_names:
            raise ValidationError(f"unknown member {key!r}", (*path, key))


def _validate_present_members(
    schema: Schema, mapping: Mapping[object, object], path: tuple[str | int, ...]
) -> tuple[Entry, ...]:
    present_members: list[Entry] = []
    for member in schema.members:
        if member.name not in mapping:
            if member.required:
                raise ValidationError(
                    f"required member {member.name!r} is missing", (*path, member.name)
                )
            continue

        present_members.append(member)
        member_path = (*path, member.name)
        _validate_member_value(member, mapping[member.name], member_path)

    return tuple(present_members)


def _validate_member_value(
    member: Entry, value: object, member_path: tuple[str | int, ...]
) -> None:
    if isinstance(member, Field):
        member.definition.validate(value, member_path)
    elif isinstance(member, Section):
        _validate_schema(member.schema, value, member_path)
    elif isinstance(member, Array):
        _validate_array(member, value, member_path)
    elif isinstance(member, Map):
        _validate_map(member, value, member_path)
    else:
        raise TypeError(f"unsupported member type: {type(member).__name__}")


def _validate_array(member: Array, value: object, path: tuple[str | int, ...]) -> None:
    if not _is_array_value(value):
        raise ValidationError("expected an array", path)
    if (minimum_length := member.minimum_length) is not None and len(
        value
    ) < minimum_length:
        raise ValidationError("array is shorter than the minimum length", path)
    if (maximum_length := member.maximum_length) is not None and len(
        value
    ) > maximum_length:
        raise ValidationError("array exceeds the maximum length", path)
    if member.unique:
        for index, element in enumerate(value):
            if any(element == previous for previous in value[:index]):
                raise ValidationError("array elements must be unique", (*path, index))

    element = member.element
    for index, item in enumerate(value):
        item_path = (*path, index)
        if isinstance(element, Definition):
            element.validate(item, item_path)
        else:
            _validate_schema(element, item, item_path)


def _validate_map(member: Map, value: object, path: tuple[str | int, ...]) -> None:
    if not isinstance(value, Mapping):
        raise ValidationError("expected a mapping", path)
    if (minimum_entries := member.minimum_entries) is not None and len(
        value
    ) < minimum_entries:
        raise ValidationError("map has fewer entries than the minimum", path)
    if (maximum_entries := member.maximum_entries) is not None and len(
        value
    ) > maximum_entries:
        raise ValidationError("map exceeds the maximum number of entries", path)

    mapping = cast("Mapping[object, object]", value)
    target = member.value
    for key, mapped_value in mapping.items():
        if type(key) is not str:
            raise ValidationError("map keys must be strings", path)
        key_path = (*path, key)
        member.key.validate(key, key_path)

        if isinstance(target, Definition):
            target.validate(mapped_value, key_path)
        else:
            _validate_schema(target, mapped_value, key_path)


def _is_array_value(value: object) -> TypeGuard[Sequence[object]]:
    return isinstance(value, Sequence) and not isinstance(
        value, (str, bytes, bytearray)
    )
