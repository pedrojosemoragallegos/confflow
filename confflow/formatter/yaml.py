from enum import Enum
from typing import Any


class SchemaKey(str, Enum):
    PROPERTIES = "properties"
    TYPE = "type"
    REQUIRED = "required"
    VALUE = "value"
    DESCRIPTION = "description"
    TITLE = "title"
    DEFAULT = "default"


def format_properties(properties: dict[str, Any], level: int = 1) -> str:
    lines: list[str] = []
    indent: str = "  " * level
    comment: str = "#"

    for name, content in properties.items():
        description: str = content.pop(SchemaKey.DESCRIPTION, "")

        if SchemaKey.PROPERTIES in content:
            lines.append(f"{indent}{name}: " + f"{comment} {description}")
            lines.append(format_properties(content[SchemaKey.PROPERTIES], level + 1))
        else:
            type: str = content.pop(SchemaKey.TYPE, "")
            required: str = str(content.pop(SchemaKey.REQUIRED, False))

            value: str = str(content.pop(SchemaKey.VALUE, ""))

            if not value:
                value = str(content.pop(SchemaKey.DEFAULT, ""))

            content.pop(SchemaKey.TITLE, None)

            conditions: str = (
                ", ".join(f"{k}: {v}" for k, v in content.items()) if content else ""
            )

            line: str = (
                f"{indent}{name}:{' ' if value else ''}{value} {comment} "
                f"{SchemaKey.TYPE}: {type}, {SchemaKey.REQUIRED}: {required}"
                f"{', ' + conditions if conditions and conditions != 'None' else ''} | {SchemaKey.DESCRIPTION}: {description}"
            )

            lines.append(line)

    return "\n".join(lines)


def format_schema(schema: dict[str, Any]) -> str:
    title: str = schema[SchemaKey.TITLE]
    properties: dict[str, Any] = schema[SchemaKey.PROPERTIES]
    result: list[str] = [f"{title}:"]
    result.append(format_properties(properties, level=1))

    return "\n".join(result)
