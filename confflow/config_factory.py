# factory.py
from typing import Any

from .config import Config, Entry
from .schema import Schema


def create_config(schema: Schema, data: dict[str, Any]) -> Config:
    items: list[Config | Entry] = []

    for key, field_or_subschema in schema.items():
        if isinstance(field_or_subschema, Schema):
            nested_config: Config = _create_nested_config(
                key, field_or_subschema, data, schema.name
            )
            items.append(nested_config)
        else:
            entry: Entry = _create_entry(key, field_or_subschema, data, schema.name)
            items.append(entry)

    return Config(schema.name, schema.description, *items)


def _create_nested_config(
    key: str, subschema: Schema, data: dict[str, Any], parent_schema_name: str
) -> Config:
    nested_data: Any = data.get(key)

    if nested_data is None:
        raise ValueError(
            f"Missing required subschema section '{key}' in '{parent_schema_name}'"
        )

    if not isinstance(nested_data, dict):
        raise ValueError(
            f"Subschema '{key}' in '{parent_schema_name}' must be a dictionary/object, "
            f"got {type(nested_data).__name__}"
        )

    nested_config: Config = create_config(subschema, nested_data)

    return Config(key, subschema.description, *nested_config.values())


def _create_entry(
    key: str, field_schema: Any, data: dict[str, Any], parent_schema_name: str
) -> Entry:
    value: Any = data.get(key, field_schema.default_value)

    if value is None and field_schema.required:
        raise ValueError(
            f"Missing required field '{key}' in section '{parent_schema_name}'"
        )

    try:
        return Entry(
            value,
            name=key,
            description=field_schema.description,
            constraints=field_schema.constraints,
        )
    except Exception as e:
        raise ValueError(
            f"Validation failed for field '{key}' in section '{parent_schema_name}': {e}"
        ) from e
