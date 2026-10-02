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


def _metadata(schema: Schema[Any], *, constraints: bool = True) -> str:
    parts = ["Optional" if schema.optional else "Required"]
    if isinstance(schema, TableArray):
        parts.extend(("repeatable", schema.name))
    elif not isinstance(schema, Table):
        parts.append(_type_name(schema))
    if isinstance(schema, Scalar) and schema.default is not None:
        parts.append(_toml_value(schema.default))
    lines = [" | ".join(parts)]
    if not constraints:
        return _comment("\n".join(lines))
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
        lines.append(_metadata(schema, constraints=not isinstance(schema, TableArray)))
        if isinstance(schema, TableArray):
            child_path = (*path, schema.name)
            sample = [
                f"[[{'.'.join(child_path)}]]",
            ]
            sample.extend(
                _comment(text)
                for constraint in schema.table.constraints
                if (text := str(constraint))
            )
            children = _render_schemas(schema.table.schemas, child_path)
            if children:
                sample.append("\n".join(children))
            content = "\n".join(
                f"# {line}" if line else "" for line in "\n".join(sample).split("\n")
            )
            sections.append(
                "\n"
                + "\n".join(lines)
                + "\n# Copy the block below to add an entry:\n"
                + "# --- <copy block> ---\n"
                + content
                + "\n# --- </copy block> ---"
            )
        elif isinstance(schema, Table):
            child_path = (*path, schema.name)
            name = ".".join(child_path)
            header = f"[{name}]"
            lines.append(header)
            sections.append("\n" + "\n".join(lines))
            children = _render_schemas(
                schema.schemas,
                child_path,
            )
            sections.extend(children)
        else:
            if isinstance(schema, Scalar) and schema.default is not None:
                assignment = _toml_assignment(schema.name, schema.default)
            else:
                assignment = f"{schema.name} ="
            lines.append(assignment)
            sections.append("\n".join(lines))
    return sections
