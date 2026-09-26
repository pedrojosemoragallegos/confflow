from __future__ import annotations

import copy
from typing import TYPE_CHECKING, cast

from confflow.core.fields import ArrayOfTables, _Table
from confflow.core.shared import ConfigurationError

if TYPE_CHECKING:
    from collections.abc import Mapping

    from confflow.core.fields import Field
    from confflow.core.schema import Schema
    from confflow.core.shared import TOMLValue

_MISSING = object()


def _resolve_source_value(
    field: Field[TOMLValue],
    name: str,
    source: Mapping[str, object],
    field_path: str,
    /,
) -> object:
    if name in source:
        return source[name]
    if field.required:
        msg = "required field is missing"
        raise ConfigurationError(field_path, msg)
    return _MISSING


def _assemble_value(
    field: Field[TOMLValue],
    field_path: str,
    validated: TOMLValue,
    /,
) -> TOMLValue:
    if isinstance(field, _Table):
        return prepare(
            field.schema,
            cast("Mapping[str, object]", validated),
            field_path,
        )
    if isinstance(field, ArrayOfTables):
        rows = cast("list[dict[str, TOMLValue]]", validated)
        return [
            prepare(
                field.schema,
                cast("Mapping[str, object]", row),
                f"{field_path}[{index}]",
            )
            for index, row in enumerate(rows)
        ]
    return copy.deepcopy(validated)


def prepare(
    schema: Schema,
    source: Mapping[str, object],
    path: str,
    /,
) -> dict[str, TOMLValue]:
    for name in source:
        if name not in schema._fields:
            unknown_path = f"{path}.{name}" if path else name
            raise ConfigurationError(unknown_path, "unknown field")

    present: frozenset[str] = frozenset(source)
    values: dict[str, TOMLValue] = {}

    for name, field in schema._fields.items():
        field_path = f"{path}.{name}" if path else name
        value = _resolve_source_value(field, name, source, field_path)
        if value is _MISSING:
            continue
        validated = field.validate(value, field_path)
        values[name] = _assemble_value(field, field_path, validated)

    for constraint in schema._constraints:
        constraint.check(values, present, path)

    return values
