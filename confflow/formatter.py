import textwrap
from datetime import date, datetime
from typing import Any, Dict, List, Set, Type, Union

from .core import Field, Schema


def format_schema(
    schema: Schema, indent_level: int = 0, max_comment_length: int = 80
) -> str:
    lines: List[str] = []
    indent: str = "  " * indent_level

    if schema.description:
        comment_lines = _format_comment(
            schema.description, indent_level, max_comment_length
        )
        lines.extend(comment_lines)

    lines.append(f"{indent}{schema.name}:")

    for field in schema.fields:
        if isinstance(field, Schema):
            nested_yaml: str = format_schema(
                field, indent_level + 1, max_comment_length
            )
            lines.extend(nested_yaml.splitlines())
        elif isinstance(field, Field):
            field_lines: List[str] = _format_field(
                field, indent_level + 1, max_comment_length
            )
            lines.extend(field_lines)
        else:
            raise TypeError(f"Unsupported field type: {type(field)}")

    return "\n".join(lines)


def _format_field(
    field: Field[Union[str, int, float, bool, datetime, bytes]],
    indent_level: int,
    max_comment_length: int = 80,
) -> List[str]:
    lines: List[str] = []
    key_indent: str = "  " * indent_level

    default_value: Any = getattr(field, "default_value", None)
    inferred_type: Type[Any] = (
        type(default_value)
        if default_value is not None
        else getattr(field, "type", str)
    )
    yaml_type: str = _python_type_to_yaml_type(inferred_type)
    constraints: List[Any] = getattr(field, "constraints", [])

    # Generate field comment
    comment_lines = _format_field_comment(
        field.description, yaml_type, constraints, indent_level, max_comment_length
    )
    lines.extend(comment_lines)

    # Field value formatting
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


def _format_comment(text: str, indent_level: int, max_length: int = 80) -> List[str]:
    """Format a basic comment with proper wrapping and indentation."""
    indent: str = "  " * indent_level
    comment_prefix: str = f"{indent}# "
    available_width: int = max_length - len(comment_prefix)

    if available_width <= 0:
        available_width = 40  # Minimum reasonable width

    wrapped_lines = textwrap.wrap(text, width=available_width)
    return [f"{comment_prefix}{line}" for line in wrapped_lines]


def _format_field_comment(
    description: str,
    yaml_type: str,
    constraints: List[Any],
    indent_level: int,
    max_length: int = 80,
) -> List[str]:
    """Format field comments with proper structure and wrapping."""
    indent: str = "  " * indent_level
    comment_prefix: str = f"{indent}# "

    lines: List[str] = []

    # Handle description
    if description:
        desc_lines = _format_comment(description, indent_level, max_length)
        lines.extend(desc_lines)

    # Type line (always on one line)
    lines.append(f"{comment_prefix}type: {yaml_type}")

    # Constraints as bullet points
    if constraints:
        lines.append(f"{comment_prefix}constraints:")
        for constraint in constraints:
            constraint_str = repr(constraint)
            lines.append(f"{comment_prefix}  - {constraint_str}")

    return lines


def _format_constraints(constraints: List[Any]) -> str:
    """Format constraints - now mainly for backwards compatibility."""
    if not constraints:
        return ""

    constraint_strs = [repr(c) for c in constraints]
    return ", ".join(constraint_strs)


def _format_structured_comment(
    sections: Dict[str, str], indent_level: int, max_length: int = 80
) -> List[str]:
    """Format multi-section comments with clear structure."""
    lines: List[str] = []
    indent: str = "  " * indent_level
    comment_prefix: str = f"{indent}# "

    for i, (section_name, content) in enumerate(sections.items()):
        if i > 0:
            lines.append(f"{indent}#")  # Empty comment line as separator

        # Section header
        lines.append(f"{comment_prefix}{section_name}:")

        # Section content
        content_lines = _format_comment(content, indent_level, max_length)
        # Remove the "# " prefix and add indented version
        for line in content_lines:
            content_without_prefix = line[len(comment_prefix) :]
            lines.append(f"{comment_prefix}  {content_without_prefix}")

    return lines


def _default_str(value: Any) -> str:
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    elif isinstance(value, str):
        return value  # no quotes
    elif isinstance(value, bool):
        return "true" if value else "false"
    elif isinstance(value, (int, float)):
        return str(value)
    elif value is None:
        return "null"
    elif isinstance(value, (list, dict, set)):
        return _format_inline(value)
    return str(value)


def _format_inline(value: Union[List[Any], Dict[Any, Any], Set[Any]]) -> str:
    if isinstance(value, list):
        formatted_items: List[str] = [_default_str(v) for v in value]
        return "[" + ", ".join(formatted_items) + "]"
    elif isinstance(value, set):
        sorted_items: List[Any] = sorted(value)
        formatted_items = [_default_str(v) for v in sorted_items]
        return "[" + ", ".join(formatted_items) + "]"
    elif isinstance(value, dict):
        formatted_pairs: List[str] = [
            f"{_default_str(k)}: {_default_str(v)}" for k, v in value.items()
        ]
        return "{" + ", ".join(formatted_pairs) + "}"
    return str(value)


def _format_complex(
    value: Union[Dict[Any, Any], List[Any], Set[Any], Any], indent_level: int = 0
) -> str:
    indent: str = "  " * indent_level
    lines: List[str] = []

    if isinstance(value, dict):
        for k, v in value.items():
            key_str: str = _default_str(k)
            value_str: str = _default_str(v)
            lines.append(f"{indent}{key_str}: {value_str}")
    elif isinstance(value, (list, set)):
        items: Union[List[Any], Set[Any]] = value
        for v in items:
            value_str = _default_str(v)
            lines.append(f"{indent}- {value_str}")
    else:
        value_str = _default_str(value)
        lines.append(f"{indent}{value_str}")

    return "\n".join(lines)


def _python_type_to_yaml_type(py_type: Type[Any]) -> str:
    type_map: Dict[Type[Any], str] = {
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
