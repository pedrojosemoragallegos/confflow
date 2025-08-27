import textwrap
from datetime import date, datetime
from typing import Any, Type, Union

from .schema import Schema
from .schema.field import Field


def format_schema(
    schema: Schema,
    indent_level: int = 0,
    max_comment_length: int = 80,
    descriptions: bool = True,
) -> str:
    lines: list[str] = []
    indent: str = "  " * indent_level

    if schema.description and descriptions:
        comment_lines = _format_comment(
            schema.description, indent_level, max_comment_length
        )
        lines.extend(comment_lines)

    lines.append(f"{indent}{schema.name}:")

    for field in schema.fields:
        if isinstance(field, Schema):
            nested_yaml: str = format_schema(
                field, indent_level + 1, max_comment_length, descriptions
            )
            lines.extend(nested_yaml.splitlines())
        elif isinstance(field, Field):
            field_lines: list[str] = _format_field(
                field, indent_level + 1, max_comment_length, descriptions
            )
            lines.extend(field_lines)
        else:
            raise TypeError(f"Unsupported field type: {type(field)}")

    return "\n".join(lines)


def _format_field(
    field: Field[Union[str, int, float, bool, datetime, bytes]],
    indent_level: int,
    max_comment_length: int = 80,
    descriptions: bool = True,
) -> list[str]:
    lines: list[str] = []
    key_indent: str = "  " * indent_level

    default_value: Any = getattr(field, "default_value", None)
    inferred_type: Type[Any] = (
        type(default_value)
        if default_value is not None
        else getattr(field, "type", str)
    )
    yaml_type: str = _python_type_to_yaml_type(inferred_type)
    constraints: list[Any] = getattr(field, "constraints", [])

    comment_lines = _format_field_comment(
        field.description if descriptions else None,
        yaml_type,
        constraints,
        indent_level,
        max_comment_length,
    )
    lines.extend(comment_lines)

    if isinstance(default_value, (dict, list, set)):
        lines.append(f"{key_indent}{field.name}:")
        formatted: str = _format_complex(default_value, indent_level + 1)
        lines.extend(formatted.splitlines())
    elif default_value is not None:
        default_str: str = _default_str(default_value)
        lines.append(f"{key_indent}{field.name}: {default_str}")
    else:
        lines.append(f"{key_indent}{field.name}:")

    return lines


def _format_comment(text: str, indent_level: int, max_length: int = 80) -> list[str]:
    indent: str = "  " * indent_level
    comment_prefix: str = f"{indent}# "
    available_width: int = max_length - len(comment_prefix)

    if available_width <= 0:
        available_width = 40

    wrapped_lines = textwrap.wrap(text, width=available_width)
    return [f"{comment_prefix}{line}" for line in wrapped_lines]


def _format_field_comment(
    description: str,
    yaml_type: str,
    constraints: list[Any],
    indent_level: int,
    max_length: int = 80,
) -> list[str]:
    indent: str = "  " * indent_level
    comment_prefix: str = f"{indent}# "

    lines: list[str] = []

    if description:
        desc_lines = _format_comment(description, indent_level, max_length)
        lines.extend(desc_lines)

    lines.append(f"{comment_prefix}type: {yaml_type}")

    if constraints:
        lines.append(f"{comment_prefix}constraints:")
        for constraint in constraints:
            constraint_str = str(constraint)
            lines.append(f"{comment_prefix}  - {constraint_str}")

    return lines


def _default_str(value: Any) -> str:
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    elif isinstance(value, str):
        return value
    elif isinstance(value, bool):
        return "true" if value else "false"
    elif isinstance(value, (int, float)):
        return str(value)
    elif value is None:
        return "null"
    elif isinstance(value, (list, dict, set)):
        return _format_inline(value)
    return str(value)


def _format_inline(value: Union[list[Any], dict[Any, Any], set[Any]]) -> str:
    if isinstance(value, list):
        formatted_items: list[str] = [_default_str(v) for v in value]
        return "[" + ", ".join(formatted_items) + "]"
    elif isinstance(value, set):
        sorted_items: list[Any] = sorted(value)
        formatted_items = [_default_str(v) for v in sorted_items]
        return "[" + ", ".join(formatted_items) + "]"
    elif isinstance(value, dict):
        formatted_pairs: list[str] = [
            f"{_default_str(k)}: {_default_str(v)}" for k, v in value.items()
        ]
        return "{" + ", ".join(formatted_pairs) + "}"
    return str(value)


def _format_complex(
    value: Union[dict[Any, Any], list[Any], set[Any], Any], indent_level: int = 0
) -> str:
    indent: str = "  " * indent_level
    lines: list[str] = []

    if isinstance(value, dict):
        for k, v in value.items():
            key_str: str = _default_str(k)
            value_str: str = _default_str(v)
            lines.append(f"{indent}{key_str}: {value_str}")
    elif isinstance(value, (list, set)):
        items: Union[list[Any], set[Any]] = value
        for v in items:
            value_str = _default_str(v)
            lines.append(f"{indent}- {value_str}")
    else:
        value_str = _default_str(value)
        lines.append(f"{indent}{value_str}")

    return "\n".join(lines)


def _python_type_to_yaml_type(py_type: Type[Any]) -> str:
    type_map: dict[Type[Any], str] = {
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
