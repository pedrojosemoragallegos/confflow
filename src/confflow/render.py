from __future__ import annotations

from typing import TYPE_CHECKING, Any

import tomlkit

from confflow.core.definitions.base import Definition
from confflow.core.definitions.date_time.offset_date_time import OffsetDateTime
from confflow.core.schemas import (
    Array,
    Mapping as MappingSchema,
    NestedArray,
    Table,
    TableArray,
)
from confflow.core.schemas.scalars.base import Scalar

if TYPE_CHECKING:
    from confflow.core.schemas.base import Schema


def render_template(
    name: str, description: str | None, schemas: tuple[Schema[Any], ...]
) -> str:
    header = _comment(f"{name.upper()}\n{description or ''}")
    body = "\n".join(_render_schemas(schemas)).lstrip("\n")
    return header + "\n\n" + (body + "\n" if body else "")


def _comment(text: str) -> str:
    return "\n".join(f"# {line}" for line in text.split("\n"))


def _metadata(schema: Schema[Any]) -> str:
    parts = ["Optional" if schema.optional else "Required"]
    if not isinstance(schema, (Table, TableArray)):
        parts.append(_type_name(schema))
    if isinstance(schema, Scalar) and schema.default is not None:
        parts.append(_toml_value(schema.default))
    lines = [" | ".join(parts)]
    if isinstance(schema, (Table, TableArray)):
        table = schema.table if isinstance(schema, TableArray) else schema
        lines.extend(text for item in table.constraints if (text := str(item)))
    else:
        definition = getattr(schema, "definition", None)
        if isinstance(definition, Definition):
            lines.extend(text for item in definition.constraints if (text := str(item)))
    return _comment("\n".join(lines))


def _type_name(schema: Schema[Any]) -> str:
    if isinstance(schema, TableArray):
        return "array of tables"
    if isinstance(schema, NestedArray):
        return f"array of {_type_name(schema.array)}"
    if isinstance(schema, MappingSchema):
        return f"mapping of {_type_name(schema.value)}"
    if isinstance(schema, Table):
        return "table"
    definition = getattr(schema, "definition", None)
    if isinstance(definition, Definition):
        names = {
            str: "string",
            int: "integer",
            float: "float",
            bool: "boolean",
        }
        name = names.get(definition.VALUE_TYPE, definition.VALUE_TYPE.__name__)
        if name == "datetime":
            name = (
                "offset datetime"
                if isinstance(definition, OffsetDateTime)
                else "local datetime"
            )
        return f"array of {name}" if isinstance(schema, Array) else name
    return "array" if isinstance(schema, Array) else "value"


def _toml_value(value: object) -> str:
    return _toml_assignment("value", value).partition(" = ")[2]


def _toml_assignment(name: str, value: object) -> str:
    return tomlkit.dumps({name: value}).rstrip("\n")


def _render_schemas(
    schemas: tuple[Schema[Any], ...],
    path: tuple[str, ...] = (),
    *,
    commented: bool = False,
) -> list[str]:
    fields = [
        schema for schema in schemas if not isinstance(schema, (Table, TableArray))
    ]
    tables = [schema for schema in schemas if isinstance(schema, (Table, TableArray))]
    sections: list[str] = []
    for schema in (*fields, *tables):
        lines = []
        if schema.description:
            lines.append(_comment(schema.description))
        lines.append(_metadata(schema))
        if isinstance(schema, (Table, TableArray)):
            section_commented = commented or schema.optional
            child_path = (*path, schema.name)
            name = ".".join(child_path)
            header = f"[[{name}]]" if isinstance(schema, TableArray) else f"[{name}]"
            lines.append(_comment(header) if section_commented else header)
            sections.append("\n" + "\n".join(lines))
            table = schema.table if isinstance(schema, TableArray) else schema
            sections.extend(
                _render_schemas(table.schemas, child_path, commented=section_commented)
            )
        else:
            if isinstance(schema, Scalar) and schema.default is not None:
                assignment = _toml_assignment(schema.name, schema.default)
                if commented:
                    assignment = _comment(assignment)
            else:
                assignment = _comment(f"{schema.name} =")
            lines.append(assignment)
            sections.append("\n".join(lines))
    return sections
