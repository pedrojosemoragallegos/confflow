from typing import get_args

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
    py_type = _get_field_type(field)
    type_str = py_type.__name__

    parts: list[str] = [f"type: {type_str}"]
    if field.default_value is not None:
        parts.append(f"default={field.default_value}")
    if field.constraints:
        parts.append(field.constraints.__class__.__name__)

    lines: list[str] = []
    if field.description:
        lines.append(f"  # {field.description}")

    lines.append(f"  # {', '.join(parts)}")

    line: str = (
        f"  {field.name}: {field.default_value}"
        if field.default_value is not None
        else f"  {field.name}:"
    )
    lines.append(line)

    return lines


def _get_field_type(field: SchemaField[Value]) -> type:
    args = get_args(field.__orig_class__)  # type: ignore
    return args[0] if args else str
