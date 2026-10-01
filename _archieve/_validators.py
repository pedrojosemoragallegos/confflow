from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, cast

from .definitions.exceptions import DefinitionError
from .exceptions import ValidationError

if TYPE_CHECKING:
    from .rules.base import Rule
    from .schemas.base import Schema


def validate_configuration(
    entries: tuple[Schema, ...], rules: tuple[Rule, ...], data: object
) -> None:
    validate_mapping(entries, rules, data)


def validate_mapping(
    entries: tuple[Schema, ...],
    rules: tuple[Rule, ...],
    data: object,
    path: tuple[str | int, ...] = (),
) -> None:
    if not isinstance(data, Mapping):
        raise ValidationError("expected a mapping", path)

    mapping = cast("Mapping[object, object]", data)
    validate_known_keys(entries, mapping, path)
    present_members = validate_present_members(entries, mapping, path)

    for rule in rules:
        rule.validate(present_members, path)


def validate_known_keys(
    entries: tuple[Schema, ...],
    mapping: Mapping[object, object],
    path: tuple[str | int, ...],
) -> None:
    member_names = {member.name for member in entries}
    for key in mapping:
        if type(key) is not str:
            raise ValidationError("member keys must be strings", path)
        if key not in member_names:
            raise ValidationError(f"unknown member {key!r}", (*path, key))


def validate_present_members(
    entries: tuple[Schema, ...],
    mapping: Mapping[object, object],
    path: tuple[str | int, ...],
) -> tuple[Schema, ...]:
    present_members: list[Schema] = []
    for member in entries:
        if member.name not in mapping:
            if not member.optional:
                raise ValidationError(
                    f"required member {member.name!r} is missing", (*path, member.name)
                )
            continue

        present_members.append(member)
        member_path = (*path, member.name)
        validate_member_value(member, mapping[member.name], member_path)

    return tuple(present_members)


def validate_member_value(
    member: Schema, value: object, member_path: tuple[str | int, ...]
) -> None:
    try:
        member.validate(value)
    except DefinitionError as error:
        raise ValidationError(str(error), member_path) from None
    except ValidationError as error:
        error_path = (*member_path, *error.path)
        raise type(error)(str(error), error_path) from None
