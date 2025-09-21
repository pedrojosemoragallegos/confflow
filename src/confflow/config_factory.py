from __future__ import annotations

import typing

from .config import Config, Entry
from .schema import Schema

if typing.TYPE_CHECKING:
    from datetime import datetime

    from .schema.field import Field


def create_config(
    schema: Schema,
    data: dict[
        str,
        list[str]
        | list[int]
        | list[float]
        | list[bool]
        | list[datetime]
        | list[bytes]
        | str
        | int
        | float
        | bool
        | datetime
        | bytes,
    ],
) -> Config:
    items: list[
        Config
        | Entry[list[str]]
        | Entry[list[int]]
        | Entry[list[float]]
        | Entry[list[bool]]
        | Entry[list[datetime]]
        | Entry[list[bytes]]
        | Entry[str]
        | Entry[int]
        | Entry[float]
        | Entry[bool]
        | Entry[datetime]
        | Entry[bytes]
    ] = []
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
            entry: (
                Entry[list[str]]
                | Entry[list[int]]
                | Entry[list[float]]
                | Entry[list[bool]]
                | Entry[list[datetime]]
                | Entry[list[bytes]]
                | Entry[str]
                | Entry[int]
                | Entry[float]
                | Entry[bool]
                | Entry[datetime]
                | Entry[bytes]
            ) = create_entry(
                key,
                field_or_subschema,
                data,
                schema.name,
            )
            items.append(entry)

    return Config(schema.name, schema.description, *items)


def _create_nested_config(
    key: str,
    subschema: Schema,
    data: dict[
        str,
        list[str]
        | list[int]
        | list[float]
        | list[bool]
        | list[datetime]
        | list[bytes]
        | str
        | int
        | float
        | bool
        | datetime
        | bytes,
    ],
    parent_schema_name: str,
) -> Config:
    nested_data: (
        list[str]
        | list[int]
        | list[float]
        | list[bool]
        | list[datetime]
        | list[bytes]
        | str
        | int
        | float
        | bool
        | datetime
        | bytes
        | dict[
            str,
            list[str]
            | list[int]
            | list[float]
            | list[bool]
            | list[datetime]
            | list[bytes]
            | str
            | int
            | float
            | bool
            | datetime
            | bytes
            | dict[
                str,
                list[str]
                | list[int]
                | list[float]
                | list[bool]
                | list[datetime]
                | list[bytes]
                | str
                | int
                | float
                | bool
                | datetime
                | bytes,
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


def create_entry(
    key: str,
    schema_field: Field[list[str]]
    | Field[list[int]]
    | Field[list[float]]
    | Field[list[bool]]
    | Field[list[datetime]]
    | Field[list[bytes]]
    | Field[str]
    | Field[int]
    | Field[float]
    | Field[bool]
    | Field[datetime]
    | Field[bytes],
    data: dict[
        str,
        list[str]
        | list[int]
        | list[float]
        | list[bool]
        | list[datetime]
        | list[bytes]
        | str
        | int
        | float
        | bool
        | datetime
        | bytes,
    ],
    parent_schema_name: str,
) -> (
    Entry[list[str]]
    | Entry[list[int]]
    | Entry[list[float]]
    | Entry[list[bool]]
    | Entry[list[datetime]]
    | Entry[list[bytes]]
    | Entry[str]
    | Entry[int]
    | Entry[float]
    | Entry[bool]
    | Entry[datetime]
    | Entry[bytes]
):
    value: (
        list[str]
        | list[int]
        | list[float]
        | list[bool]
        | list[datetime]
        | list[bytes]
        | str
        | int
        | float
        | bool
        | datetime
        | bytes
        | None
    ) = data.get(key, schema_field.default_value)

    if value is None:
        raise ValueError(  # noqa: TRY003
            f"No value provided for field '{key}' in section '{parent_schema_name}' "  # noqa: EM102
            f"and no default value specified",
        )

    try:
        return Entry(
            value,  # type: ignore
            name=key,
            description=schema_field.description,
            constraints=schema_field.constraints,  # type: ignore
        )
    except Exception as e:  # TODO correct error
        raise ValueError(  # noqa: TRY003
            f"Validation failed for field '{key}' in section '{parent_schema_name}': {e}",  # noqa: E501, EM102
        ) from e
