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
    del name
    header = _comment(description) if description else ""
    body = "\n".join(_render_schemas(schemas)).lstrip("\n")
    prefix = header + "\n\n" if header else ""
    return prefix + (body + "\n" if body else "")


def _comment(text: str) -> str:
    return "\n".join(f"# {line}" for line in text.split("\n"))


def _metadata(schema: Schema[Any], *, constraints: bool = True) -> str:
    parts = ["Optional" if schema.optional else "Required"]
    if isinstance(schema, TableArray):
        parts.append("list")
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
        return "list of tables"
    if isinstance(schema, NestedArray):
        return f"list of {_type_name(schema.array)}"
    if isinstance(schema, MappingSchema):
        return "mapping"
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
        return f"list of {name}" if isinstance(schema, Array) else name
    return "list" if isinstance(schema, Array) else "value"


def _toml_value(value: object) -> str:
    return _toml_assignment("value", value).partition(" = ")[2]


def _toml_assignment(name: str, value: object) -> str:
    return tomlkit.dumps({name: value}).rstrip("\n")


def _copy_block(
    content: str,
    *,
    label: str = "copy block",
    instruction: bool = True,
) -> str:
    commented = "\n".join(
        f"# {line}" if line else "" for line in content.split("\n")
    )
    lines = [f"# --- <{label}> ---", commented, f"# --- </{label}> ---"]
    if instruction:
        lines.insert(0, "# Copy the block below to add an entry:")
    return "\n".join(lines)


def _render_mapping(schema: MappingSchema, path: tuple[str, ...]) -> str:
    name = ".".join((*path, schema.name))
    lines = []
    if schema.description:
        lines.append(_comment(schema.description))
    lines.extend((_metadata(schema), f"[{name}]"))

    value = schema.value
    sample: list[str] = []
    if value.description:
        sample.append(_comment(value.description))
    sample.append(_metadata(value))
    if isinstance(value, Table):
        entry_path = (*path, schema.name, "<key>")
        sample.append(f"[{'.'.join(entry_path)}]")
        sample.extend(_render_schemas(value.schemas, entry_path))
    elif isinstance(value, Scalar) and value.default is not None:
        sample.append(f"<key> = {_toml_value(value.default)}")
    else:
        sample.append("<key> =")

    return (
        "\n"
        + "\n".join(lines)
        + "\n"
        + _copy_block(
            "\n".join(sample),
            label="copy this block",
            instruction=False,
        )
    )


def _render_schemas(
    schemas: tuple[Schema[Any], ...],
    path: tuple[str, ...] = (),
) -> list[str]:
    fields = [
        schema
        for schema in schemas
        if not isinstance(schema, (Table, TableArray, MappingSchema))
    ]
    tables = [
        schema
        for schema in schemas
        if isinstance(schema, (Table, TableArray, MappingSchema))
    ]
    sections: list[str] = []
    for schema in (*fields, *tables):
        if isinstance(schema, MappingSchema):
            sections.append(_render_mapping(schema, path))
            continue

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
            sections.append(
                "\n"
                + "\n".join(lines)
                + "\n"
                + _copy_block("\n".join(sample))
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
