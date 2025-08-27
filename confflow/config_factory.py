from typing import Any, Union

from .config import Config, Entry
from .schema import Schema
from .schema.field import Field


def create_config(schema: Schema, data: dict[str, Any]) -> Config:
    items: list[Union[Config, Entry]] = []

    for key, field_or_subschema in schema.items():
        if isinstance(field_or_subschema, Schema):
            nested_config: Config = _create_nested_config(
                key, field_or_subschema, data, schema.name
            )
            items.append(nested_config)
        else:
            entry: Entry = create_entry(key, field_or_subschema, data, schema.name)
            items.append(entry)

    return Config(schema.name, schema.description, *items)


def _create_nested_config(
    key: str, subschema: Schema, data: dict[str, Any], parent_schema_name: str
) -> Config:
    nested_data: Any = data.get(key)

    if nested_data is None:
        raise ValueError(f"Missing subschema section '{key}' in '{parent_schema_name}'")
    if not isinstance(nested_data, dict):
        raise ValueError(
            f"Subschema '{key}' in '{parent_schema_name}' must be a dictionary/object, "
            f"got {type(nested_data).__name__}"
        )

    nested_config: Config = create_config(subschema, nested_data)

    return Config(key, subschema.description, *nested_config.values())


def create_entry(
    key: str, schema_field: Field, data: dict[str, Any], parent_schema_name: str
) -> Entry:
    value: Any = data.get(key, schema_field.default_value)

    if value is None:
        raise ValueError(
            f"No value provided for field '{key}' in section '{parent_schema_name}' "
            f"and no default value specified"
        )
    try:
        return Entry(
            value,
            name=key,
            description=schema_field.description,
            constraints=schema_field.constraints,
        )
    except Exception as e:
        raise ValueError(
            f"Validation failed for field '{key}' in section '{parent_schema_name}': {e}"
        ) from e
