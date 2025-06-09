from typing import get_args

import yaml

from .core import Schema, SchemaField
from .types import Value


def format_schema(schema: Schema) -> str:
    lines: list[str] = []

    if schema.description:
        lines.append(f"# {schema.description}")

    lines.append(f"{schema.name}:")

    for field in schema.fields:
        lines.extend(_format_field(field))

    return "\n".join(lines)


def _format_field(field: SchemaField[Value]) -> list[str]:
    lines: list[str] = []
    indent: str = "  "
    key_indent: str = indent
    value_indent: str = indent * 2

    if field.description:
        lines.append(f"{key_indent}# {field.description}")

    parts: list[str] = [f"type: {_get_field_type(field).__name__}"]
    if field.default_value is not None:
        parts.append(f"default={field.default_value}")
    if field.constraints:
        parts.append(field.constraints.__class__.__name__)
    lines.append(f"{key_indent}# {', '.join(parts)}")

    if field.default_value is not None:
        if isinstance(field.default_value, (dict, list, set)):
            lines.append(f"{key_indent}{field.name}:")
            dumped: str = yaml.safe_dump(
                field.default_value, default_flow_style=False
            ).rstrip()
            for line in dumped.splitlines():
                lines.append(f"{value_indent}{line}")
        else:
            lines.append(f"{key_indent}{field.name}: {field.default_value}")
    else:
        lines.append(f"{key_indent}{field.name}:")

    return lines


def _get_field_type(field: SchemaField[Value]) -> type:
    args = get_args(field.__orig_class__)  # type: ignore
    return args[0] if args else str
