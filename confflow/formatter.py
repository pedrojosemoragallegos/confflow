from datetime import date, datetime
from typing import Any

from .core import Schema, SchemaField
from .types import Value


def format_schema(schema: Schema, indent_level: int = 0) -> str:
    lines: list[str] = []
    indent: str = "  " * indent_level

    if schema.description:
        lines.append(f"{indent}# {schema.description}")

    lines.append(f"{indent}{schema.name}:")

    for field in schema.fields:
        if isinstance(field, Schema):
            nested_yaml = format_schema(field, indent_level + 1)
            lines.extend(nested_yaml.splitlines())
        elif isinstance(field, SchemaField):
            lines.extend(_format_field(field, indent_level + 1))
        else:
            raise TypeError(f"Unsupported field type: {type(field)}")

    return "\n".join(lines)


def _format_field(field: SchemaField[Value], indent_level: int) -> list[str]:
    lines: list[str] = []
    key_indent = "  " * indent_level

    default_value = getattr(field, "default_value", None)
    inferred_type = (
        type(default_value)
        if default_value is not None
        else getattr(field, "type", str)
    )
    yaml_type = _python_type_to_yaml_type(inferred_type)
    constraints_info = _format_constraints(getattr(field, "constraints", []))

    # Build the comment
    comment_parts = []
    if field.description:
        comment_parts.append(field.description)
    comment_parts.append(f"type: {yaml_type}")
    if constraints_info:
        comment_parts.append(f"constraints: {constraints_info}")
    comment_line = f"{key_indent}# {' | '.join(comment_parts)}"
    lines.append(comment_line)

    # Field value formatting
    if isinstance(default_value, (dict, list, set)):
        lines.append(f"{key_indent}{field.name}:")
        formatted = _format_complex(default_value, indent_level + 1)
        lines.extend(formatted.splitlines())
    elif default_value is not None:
        lines.append(f"{key_indent}{field.name}: {_default_str(default_value)}")
    else:
        lines.append(f"{key_indent}{field.name}:")

    return lines


def _format_constraints(constraints: list[Any]) -> str:
    return ", ".join(repr(c) for c in constraints)


def _default_str(value: Any) -> str:
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    elif isinstance(value, str):
        return value  # No quotes
    elif isinstance(value, bool):
        return "true" if value else "false"
    elif isinstance(value, (int, float)):
        return str(value)
    elif value is None:
        return "null"
    elif isinstance(value, (list, dict, set)):
        return _format_inline(value)
    return str(value)


def _format_inline(value: Any) -> str:
    if isinstance(value, list):
        return "[" + ", ".join(_default_str(v) for v in value) + "]"
    elif isinstance(value, set):
        return "[" + ", ".join(_default_str(v) for v in sorted(value)) + "]"
    elif isinstance(value, dict):
        return (
            "{"
            + ", ".join(
                f"{_default_str(k)}: {_default_str(v)}" for k, v in value.items()
            )
            + "}"
        )
    return str(value)


def _format_complex(value: Any, indent_level: int = 0) -> str:
    indent = "  " * indent_level
    lines: list[str] = []

    if isinstance(value, dict):
        for k, v in value.items():
            lines.append(f"{indent}{_default_str(k)}: {_default_str(v)}")
    elif isinstance(value, (list, set)):
        for v in value:
            lines.append(f"{indent}- {_default_str(v)}")
    else:
        lines.append(f"{indent}{_default_str(value)}")

    return "\n".join(lines)


def _python_type_to_yaml_type(py_type: Any) -> str:
    type_map = {
        str: "string",
        int: "integer",
        float: "float",
        bool: "boolean",
        list: "array",
        dict: "object",
        set: "array",
        date: "timestamp",
        datetime: "timestamp",
        type(None): "null",
    }
    return type_map.get(py_type, "string")
