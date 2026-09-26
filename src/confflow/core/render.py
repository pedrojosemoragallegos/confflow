from __future__ import annotations

import copy
import os
import tempfile
import textwrap
from pathlib import Path
from typing import TYPE_CHECKING

import tomlkit

from confflow.core.constraint import Constraint, _Constraint
from confflow.core.fields import ArrayOfTables, Field, _Table

if TYPE_CHECKING:
    from confflow.core.schema import Schema
    from confflow.core.shared import TOMLValue

_PRESENCE_DESCRIPTIONS = {
    "AllOrNone": (
        "Either all fields in this group must be set, or none of them may be set."
    ),
    "Exclusive": "At most one field in this group may be set.",
    "ExactlyOne": "Exactly one field in this group must be set.",
    "AtLeastOne": "At least one field in this group must be set.",
}

_COMPARISON_DESCRIPTIONS = {
    "Requires": 'If "{0}" is set, "{1}" must also be set.',
    "Equal": '"{0}" and "{1}" must have equal values.',
    "NotEqual": '"{0}" and "{1}" must have different values.',
    "LessThan": '"{0}" must be less than "{1}".',
    "LessThanOrEqual": '"{0}" must be less than or equal to "{1}".',
    "GreaterThan": '"{0}" must be greater than "{1}".',
    "GreaterThanOrEqual": '"{0}" must be greater than or equal to "{1}".',
}


def _display(value: object, /) -> str:
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, type):
        return value.__name__
    return repr(value)


def _own_option_parts(field: Field[TOMLValue], /) -> list[str]:
    parts: list[str] = ["required" if field.required else "optional"]
    if field.default is not None:
        parts.append(f"default={_display(field.default)}")
    for name in field.option_names:
        value = getattr(field, name)
        if value is not None:
            parts.append(f"{name}={_display(value)}")
    return parts


def _element_option_parts(element: Field[TOMLValue], /) -> list[str]:
    parts: list[str] = []
    for name in element.option_names:
        value = getattr(element, name)
        if value is not None:
            parts.append(f"element.{name}={_display(value)}")
    return parts


def _field_options(field: Field[TOMLValue], /) -> list[str]:
    element = getattr(field, "element", None)
    type_name = type(field).__name__.lower()
    if isinstance(element, Field):
        type_name += f"[{type(element).__name__.lower()}]"

    parts: list[str] = [type_name, *_own_option_parts(field)]
    if isinstance(element, Field):
        parts.extend(_element_option_parts(element))
    return parts


def _comment_block(field: Field[TOMLValue], /, *, width: int = 100) -> list[str]:
    content_width = width - 2
    description = field.description or field.name
    lines = [
        f"# {line}" for line in textwrap.wrap(description, width=content_width) or [""]
    ]
    parts = _field_options(field)

    if not parts:
        return lines

    current = "# "
    for part in parts:
        token = part if current == "# " else f" | {part}"
        if len(current) + len(token) <= width:
            current += token
            continue

        if current != "# ":
            lines.append(current)

        wrapped = textwrap.wrap(
            part,
            width=content_width,
            break_long_words=True,
            break_on_hyphens=False,
        ) or [""]
        lines.extend(f"# {piece}" for piece in wrapped[:-1])
        current = f"# {wrapped[-1]}"

    if current != "# ":
        lines.append(current)

    return lines


def _field_comment_lines(field: Field[TOMLValue], /) -> list[str]:
    return _comment_block(field)


def _toml_item(value: TOMLValue, /) -> object:
    if type(value) is dict:
        item = tomlkit.inline_table()
        for key, nested in value.items():
            item[key] = _toml_item(nested)
        return item
    if type(value) is list:
        array = tomlkit.array()
        for nested in value:
            array.append(_toml_item(nested))
        return array
    return value


def _toml_literal(value: TOMLValue, /) -> str:
    return tomlkit.dumps({"value": _toml_item(value)}).strip().removeprefix("value = ")


def _section(title: str, /, *, width: int = 100) -> str:
    return "# " + f" {title} ".center(width - 2, "─")


def _constraint_title(constraint: Constraint, /) -> str:
    if isinstance(constraint, _Constraint):
        return {
            "AllOrNone": "ALL OR NONE",
            "Exclusive": "EXCLUSIVE",
            "ExactlyOne": "EXACTLY ONE",
            "AtLeastOne": "AT LEAST ONE",
            "Requires": "REQUIRES",
            "Equal": "EQUAL",
            "NotEqual": "NOT EQUAL",
            "LessThan": "LESS THAN",
            "LessThanOrEqual": "LESS THAN OR EQUAL",
            "GreaterThan": "GREATER THAN",
            "GreaterThanOrEqual": "GREATER THAN OR EQUAL",
        }.get(constraint.name, constraint.name.upper())
    return type(constraint).__name__.upper()


def _constraint_description(constraint: Constraint, /) -> str:
    if not isinstance(constraint, _Constraint):
        return constraint.describe()
    names = [target.name for target in constraint.targets]
    if constraint.name in _PRESENCE_DESCRIPTIONS:
        return _PRESENCE_DESCRIPTIONS[constraint.name]
    if constraint.name in _COMPARISON_DESCRIPTIONS:
        return _COMPARISON_DESCRIPTIONS[constraint.name].format(*names)
    return constraint.describe()


def _render_field(field: Field[TOMLValue], /) -> list[str]:
    lines = _field_comment_lines(field)
    if field.default is None:
        lines.append(f"{field.name} =")
    else:
        lines.append(f"{field.name} = {_toml_literal(copy.deepcopy(field.default))}")
    lines.append("")
    return lines


def _comment_lines(text: str, /, *, width: int = 98) -> list[str]:
    return [f"# {line}" for line in textwrap.wrap(text, width=width) or [""]]


def _table_comment_lines(text: str, field: _Table, /) -> list[str]:
    lines = _comment_lines(text)
    if field.required:
        lines.append("# required")
    return lines


def _nested_block(
    comment_lines: list[str],
    header: str,
    body: list[str],
    /,
) -> list[str]:
    return [*comment_lines, header, *body, ""]


def _render_target_lines(
    schema: Schema,
    target: Field[TOMLValue] | Schema,
    prefix: str,
    /,
) -> list[str] | None:
    table_name = f"{prefix}.{target.name}" if prefix else target.name

    if not isinstance(target, Field):
        field = schema._fields[target.name]
        if not isinstance(field, _Table) or field.schema is not target:
            return None
        return _nested_block(
            _table_comment_lines(target.description or target.name, field),
            f"[{table_name}]",
            template_lines(target, prefix=table_name),
        )
    if isinstance(target, _Table):
        return _nested_block(
            _table_comment_lines(target.description or target.name, target),
            f"[{table_name}]",
            template_lines(target.schema, prefix=table_name),
        )
    if isinstance(target, ArrayOfTables):
        return _nested_block(
            _field_comment_lines(target),
            f"[[{table_name}]]",
            template_lines(target.schema, prefix=table_name),
        )
    return _render_field(target)


def _append_target_lines(
    schema: Schema,
    target: Field[TOMLValue] | Schema,
    prefix: str,
    rendered: set[str],
    lines: list[str],
    /,
) -> None:
    if target.name in rendered:
        return
    new_lines = _render_target_lines(schema, target, prefix)
    if new_lines is None:
        return
    lines.extend(new_lines)
    rendered.add(target.name)


def _constraint_block_lines(
    schema: Schema,
    item: Constraint,
    index: int,
    constrained_at: dict[str, int],
    prefix: str,
    rendered: set[str],
    /,
) -> list[str]:
    title = _constraint_title(item)
    lines = [
        _section(title),
        *_comment_lines(_constraint_description(item)),
        "",
    ]
    for target in item.targets:
        if constrained_at.get(target.name) == index:
            _append_target_lines(schema, target, prefix, rendered, lines)
    lines.append(_section(f"END {title}"))
    lines.append("")
    return lines


def template_lines(
    schema: Schema,
    /,
    *,
    prefix: str = "",
    top: bool = False,
) -> list[str]:
    lines: list[str] = []
    rendered: set[str] = set()

    if top:
        lines.extend(_comment_lines(schema.description or schema.name))
        lines.append("")

    constrained_at: dict[str, int] = {}
    for index, item in enumerate(schema._items):
        if isinstance(item, Constraint):
            for target in item.targets:
                constrained_at.setdefault(target.name, index)

    for index, item in enumerate(schema._items):
        if isinstance(item, Constraint):
            lines.extend(
                _constraint_block_lines(
                    schema,
                    item,
                    index,
                    constrained_at,
                    prefix,
                    rendered,
                ),
            )
        elif constrained_at.get(item.name, index) <= index:
            _append_target_lines(schema, item, prefix, rendered, lines)

    while lines and lines[-1] == "":
        lines.pop()

    return lines


def atomic_write(path: Path, content: str, /, *, parents: bool = True) -> None:
    if parents:
        path.parent.mkdir(parents=True, exist_ok=True)
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="\n",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            temporary = Path(handle.name)
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        if path.exists():
            temporary.chmod(path.stat().st_mode & 0o777)
        temporary.replace(path)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()
