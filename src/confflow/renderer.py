from __future__ import annotations

from collections.abc import Callable
from datetime import date, datetime, time
from json import dumps as json_dumps
from math import isinf
from typing import TYPE_CHECKING

from .core.definitions.boolean import Boolean as BooleanField
from .core.definitions.boolean_literal import BooleanLiteral
from .core.definitions.decimal import Decimal as DecimalField
from .core.definitions.decimal_literal import DecimalLiteral
from .core.definitions.local_date import LocalDate as LocalDateField
from .core.definitions.local_date_literal import LocalDateLiteral
from .core.definitions.local_date_time import LocalDateTime as LocalDateTimeField
from .core.definitions.local_date_time_literal import LocalDateTimeLiteral
from .core.definitions.local_time import LocalTime as LocalTimeField
from .core.definitions.local_time_literal import LocalTimeLiteral
from .core.definitions.number import Number as NumberField
from .core.definitions.number_literal import NumberLiteral
from .core.definitions.offset_date_time import OffsetDateTime as OffsetDateTimeField
from .core.definitions.offset_date_time_literal import OffsetDateTimeLiteral
from .core.definitions.text import Text as TextField
from .core.definitions.text_literal import TextLiteral
from .core.members.array import Array
from .core.members.field import Field
from .core.members.map import Map
from .core.members.section import Section
from .core.rules.all_or_none import AllOrNone
from .core.rules.at_least_one_of import AtLeastOneOf
from .core.rules.exactly_one_of import ExactlyOneOf
from .core.rules.forbids import Forbids
from .core.rules.forbids_any import ForbidsAny
from .core.rules.mutually_exclusive import MutuallyExclusive
from .core.rules.requires import Requires
from .core.rules.requires_all import RequiresAll
from .core.rules.requires_any import RequiresAny
from .core.schema import Schema

if TYPE_CHECKING:
    from .core.definitions.base import Definition, TomlScalar
    from .core.members.base import Entry
    from .core.rules.base import Rule

_ScalarFormatter = Callable[[object], str]


def _render_description(description: str) -> list[str]:
    return [f"# {line}" if line else "#" for line in description.splitlines()]


def _render_metadata(member: Entry, format_scalar: _ScalarFormatter) -> list[str]:
    lines: list[str] = []
    if member.description:
        lines.extend(_render_description(member.description))

    presence = "required" if member.required else "optional"
    metadata = f"# {presence} | {_type_name(member)}"
    if isinstance(member, Field) and member.default is not None:
        metadata += f" | default: {format_scalar(member.default)}"
    lines.append(metadata)
    return lines


def _type_name(member: Entry) -> str:
    if isinstance(member, Field):
        return field__type_name(member)
    if isinstance(member, Section):
        return member.schema.name
    if isinstance(member, Array):
        collection_name = "set" if member.unique else "list"
        return f"{_target_name(member.element)} {collection_name}"
    if isinstance(member, Map):
        return f"{_target_name(member.value)} mapping"
    return type(member).__name__


def field__type_name(field: Field[TomlScalar]) -> str:
    concrete_name = type(field).__name__
    if (literal_type := _literal__type_name(field)) is not None:
        literal_class, literal_name = literal_type
        return (
            literal_name
            if type(field) is literal_class
            else f"{concrete_name} ({literal_name})"
        )
    if (root := _scalar_root(field)) is None:
        return concrete_name

    root_type, root_name = root
    return root_name if type(field) is root_type else f"{concrete_name} ({root_name})"


def _target_name(target: Definition[TomlScalar] | Schema) -> str:
    if isinstance(target, Schema):
        return target.name
    if isinstance(target, Field):
        return field__type_name(target)
    return type(target).__name__


def _render_member_rules(member: Entry, rules: tuple[Rule, ...]) -> list[str]:
    return [f"# {_rule_text(rule)}" for rule in rules if member in rule.members]


_SCALAR_FIELD_TYPES: tuple[tuple[type[object], str], ...] = (
    (TextField, "Text"),
    (NumberField, "Number"),
    (DecimalField, "Decimal"),
    (BooleanField, "Bool"),
    (OffsetDateTimeField, "OffsetDateTime"),
    (LocalDateTimeField, "LocalDateTime"),
    (LocalDateField, "LocalDate"),
    (LocalTimeField, "LocalTime"),
)


def _scalar_root(field: Field[TomlScalar]) -> tuple[type[object], str] | None:
    for field_type, name in _SCALAR_FIELD_TYPES:
        if isinstance(field, field_type):
            return field_type, name
    return None


_LITERAL_FIELD_TYPES: tuple[tuple[type[object], str], ...] = (
    (TextLiteral, "Text Literal"),
    (NumberLiteral, "Number Literal"),
    (DecimalLiteral, "Decimal Literal"),
    (BooleanLiteral, "Boolean Literal"),
    (OffsetDateTimeLiteral, "Offset Date Time Literal"),
    (LocalDateTimeLiteral, "Local Date Time Literal"),
    (LocalDateLiteral, "Local Date Literal"),
    (LocalTimeLiteral, "Local Time Literal"),
)


def _literal__type_name(field: Field[TomlScalar]) -> tuple[type[object], str] | None:
    for literal_type, name in _LITERAL_FIELD_TYPES:
        if isinstance(field, literal_type):
            return literal_type, name
    return None


def _rule_text(rule: Rule) -> str:
    return _group_rule_text(rule) or _directional_rule_text(rule) or type(rule).__name__


def _group_rule_text(rule: Rule) -> str | None:
    if isinstance(rule, MutuallyExclusive):
        return f"at most one of {_member_list(rule.members)} may be present."
    if isinstance(rule, ExactlyOneOf):
        return f"exactly one of {_member_list(rule.members)} must be present."
    if isinstance(rule, AtLeastOneOf):
        return f"at least one of {_member_list(rule.members)} must be present."
    if isinstance(rule, AllOrNone):
        return (
            f"{_member_list(rule.members)} must either all be present or all be absent."
        )
    return None


def _directional_rule_text(rule: Rule) -> str | None:
    if isinstance(rule, Requires):
        return f"{rule.source.name} requires {rule.target.name}."
    if isinstance(rule, RequiresAny):
        return (
            f"{rule.source.name} requires at least one of {_member_list(rule.targets)}."
        )
    if isinstance(rule, RequiresAll):
        return f"{rule.source.name} requires all of {_member_list(rule.targets)}."
    if isinstance(rule, Forbids):
        return f"{rule.source.name} forbids {rule.target.name}."
    if isinstance(rule, ForbidsAny):
        return f"{rule.source.name} forbids any of {_member_list(rule.targets)}."
    return None


def _member_list(members: tuple[Entry, ...]) -> str:
    return f"[{', '.join(member.name for member in members)}]"


def render(schema: Schema) -> str:
    if not isinstance(schema, Schema):
        raise TypeError("schema must be a Schema")

    lines = [f"# {schema.name}"]
    if schema.description:
        lines.extend(_render_description(schema.description))
    lines.append("")
    lines.extend(_render_schema(schema).splitlines())
    return "\n".join(lines).rstrip() + "\n"


def _render_schema(schema: Schema, prefix: tuple[str, ...] = ()) -> str:
    return "\n".join(_render_schema_members(schema, prefix))


def _render_schema_members(schema: Schema, prefix: tuple[str, ...] = ()) -> list[str]:
    lines: list[str] = []
    for index, member in enumerate(schema.members):
        lines.extend(_render_member(member, prefix, schema.rules))
        if index != len(schema.members) - 1:
            lines.append("")
    return lines


def _render_member(
    member: Entry,
    prefix: tuple[str, ...],
    rules: tuple[Rule, ...],
) -> list[str]:
    lines = _render_metadata(member, _format_toml_scalar)
    lines.extend(_render_member_rules(member, rules))

    if isinstance(member, Field):
        member_path = (*prefix, member.name)
        lines.append(f"{'.'.join(member_path)} = {_format_default(member.default)}")
        return lines

    if isinstance(member, Section):
        section_path = (*prefix, member.name)
        if member.schema.description:
            lines.extend(_render_description(member.schema.description))
        nested = _render_schema(member.schema, section_path)
        if nested:
            lines.extend(nested.splitlines())
        return lines

    if isinstance(member, Array):
        if isinstance(member.element, Schema):
            section_path = (*prefix, member.name)
            lines.extend(
                _render_commented_schema_template(
                    member.element,
                    f"[[{'.'.join(section_path)}]]",
                ),
            )
        else:
            member_path = (*prefix, member.name)
            lines.append(f"# {'.'.join(member_path)} = ")
        return lines

    if isinstance(member, Map):
        map_path = (*prefix, member.name)
        if isinstance(member.value, Schema):
            template_path = (*map_path, "<key>")
            lines.extend(
                _render_commented_schema_template(
                    member.value,
                    f"[{'.'.join(template_path)}]",
                ),
            )
        else:
            lines.append(f"# {'.'.join((*map_path, '<key>'))} = ")
        return lines

    raise TypeError(f"unsupported member type: {type(member).__name__}")


def _render_commented_schema_template(schema: Schema, header: str) -> list[str]:
    lines: list[str] = [f"# --- {schema.name} ---"]
    if schema.description:
        lines.extend(_render_description(schema.description))
    lines.append(f"# {header}")
    lines.append("")
    lines.extend(_comment_schema_members(schema))
    lines.append(f"# --- end {schema.name} ---")
    return lines


def _comment_schema_members(schema: Schema) -> list[str]:
    lines: list[str] = []
    for line in _render_schema_members(schema):
        lines.append("") if not line else lines.append(f"# {line.removeprefix('# ')}")
    return lines


def _format_default(value: object | None) -> str:
    return "" if value is None else _format_toml_scalar(value)


def _format_toml_scalar(value: object) -> str:
    if type(value) is str:
        return json_dumps(value, ensure_ascii=False)
    if type(value) is bool:
        return "true" if value else "false"
    if type(value) is int:
        return str(value)
    if type(value) is float:
        if isinf(value):
            return "inf" if value > 0 else "-inf"
        return repr(value)
    if type(value) is datetime or type(value) is date or type(value) is time:
        return value.isoformat()
    raise TypeError(f"unsupported TOML scalar type: {type(value).__name__}")
