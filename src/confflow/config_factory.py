from __future__ import annotations

import typing

from .config import Config, Entry
from .schema import Field, Schema

if typing.TYPE_CHECKING:
    from datetime import datetime

    from .types import EntryTypes, FieldTypes, ValueTypes


def _create_nested_config(
    key: str,
    subschema: Schema,
    data: dict[str, ValueTypes],
    parent_schema_name: str,
) -> Config:
    nested_data: (
        ValueTypes
        | dict[
            str,
            ValueTypes
            | dict[
                str,
                ValueTypes,
            ],
        ]
    ) = data[key]

    if not isinstance(nested_data, dict):
        raise TypeError(  # noqa: TRY003
            f"Subschema '{key}' in '{parent_schema_name}' must be a dictionary/object, "  # noqa: EM102
            f"got {type(nested_data).__name__}",
        )

    nested_config: Config = create_config(subschema, nested_data)

    return Config(key, subschema.description, *nested_config.values())


def create_config(
    schema: Schema,
    data: dict[
        str,
        ValueTypes,
    ],
) -> Config:
    items: list[Config | EntryTypes] = []
    for key, field_or_subschema in schema.items():
        if isinstance(field_or_subschema, Schema):
            nested_config: Config = _create_nested_config(
                key,
                field_or_subschema,
                data,
                schema.name,
            )
            items.append(nested_config)
        else:
            entry: EntryTypes = create_entry(
                key,
                field_or_subschema,
                data,
                schema.name,
            )
            items.append(entry)

    return Config(schema.name, schema.description, *items)


@typing.overload
def create_entry(
    key: str,
    schema_field: Field[str],
    data: dict[str, ValueTypes],
    parent_schema_name: str,
) -> Entry[str]: ...
@typing.overload
def create_entry(
    key: str,
    schema_field: Field[int],
    data: dict[str, ValueTypes],
    parent_schema_name: str,
) -> Entry[int]: ...
@typing.overload
def create_entry(
    key: str,
    schema_field: Field[float],
    data: dict[str, ValueTypes],
    parent_schema_name: str,
) -> Entry[float]: ...
@typing.overload
def create_entry(
    key: str,
    schema_field: Field[bool],
    data: dict[str, ValueTypes],
    parent_schema_name: str,
) -> Entry[bool]: ...
@typing.overload
def create_entry(
    key: str,
    schema_field: Field[datetime],
    data: dict[str, ValueTypes],
    parent_schema_name: str,
) -> Entry[datetime]: ...
@typing.overload
def create_entry(
    key: str,
    schema_field: Field[bytes],
    data: dict[str, ValueTypes],
    parent_schema_name: str,
) -> Entry[bytes]: ...
@typing.overload
def create_entry(
    key: str,
    schema_field: Field[list[str]],
    data: dict[str, ValueTypes],
    parent_schema_name: str,
) -> Entry[list[str]]: ...
@typing.overload
def create_entry(
    key: str,
    schema_field: Field[list[int]],
    data: dict[str, ValueTypes],
    parent_schema_name: str,
) -> Entry[list[int]]: ...
@typing.overload
def create_entry(
    key: str,
    schema_field: Field[list[float]],
    data: dict[str, ValueTypes],
    parent_schema_name: str,
) -> Entry[list[float]]: ...
@typing.overload
def create_entry(
    key: str,
    schema_field: Field[list[bool]],
    data: dict[str, ValueTypes],
    parent_schema_name: str,
) -> Entry[list[bool]]: ...
@typing.overload
def create_entry(
    key: str,
    schema_field: Field[list[datetime]],
    data: dict[str, ValueTypes],
    parent_schema_name: str,
) -> Entry[list[datetime]]: ...
@typing.overload
def create_entry(
    key: str,
    schema_field: Field[list[bytes]],
    data: dict[str, ValueTypes],
    parent_schema_name: str,
) -> Entry[list[bytes]]: ...
def create_entry(
    key: str,
    schema_field: FieldTypes,
    data: dict[str, ValueTypes],
    parent_schema_name: str,
) -> EntryTypes:
    value: ValueTypes | None = data.get(key, schema_field.default_value)

    if value is None:
        raise ValueError(  # noqa: TRY003
            f"No value provided for field '{key}' in section '{parent_schema_name}' "  # noqa: EM102
            f"and no default value specified",
        )

    try:
        return Entry(
            typing.cast("typing.Any", value),
            name=key,
            description=schema_field.description,
            constraints=typing.cast("typing.Any", schema_field.constraints),
        )
    except Exception as e:
        raise ValueError(  # noqa: TRY003
            f"Validation failed for field '{key}' in section '{parent_schema_name}': {e}",  # noqa: E501, EM102
        ) from e
