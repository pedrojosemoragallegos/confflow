from __future__ import annotations

from collections.abc import Callable
from datetime import date, datetime, time
from json import dumps as json_dumps
from math import isinf
from typing import TYPE_CHECKING

from .core.entries.array import Array
from .core.entries.mapping import Mapping
from .core.entries.scalars.base import Scalar
from .core.entries.scalars.boolean import Boolean as BooleanField
from .core.entries.scalars.decimal import Decimal as DecimalField
from .core.entries.scalars.literals.decimal import DecimalLiteral
from .core.entries.scalars.literals.local_date import LocalDateLiteral
from .core.entries.scalars.literals.local_date_time import LocalDateTimeLiteral
from .core.entries.scalars.literals.local_time import LocalTimeLiteral
from .core.entries.scalars.literals.number import NumberLiteral
from .core.entries.scalars.literals.offset_date_time import OffsetDateTimeLiteral
from .core.entries.scalars.literals.text import TextLiteral
from .core.entries.scalars.local_date import LocalDate as LocalDateField
from .core.entries.scalars.local_date_time import LocalDateTime as LocalDateTimeField
from .core.entries.scalars.local_time import LocalTime as LocalTimeField
from .core.entries.scalars.number import Number as NumberField
from .core.entries.scalars.offset_date_time import OffsetDateTime as OffsetDateTimeField
from .core.entries.scalars.text import Text as TextField
from .core.entries.table import Table
from .core.rules.all_or_none import AllOrNone
from .core.rules.at_least_one_of import AtLeastOneOf
from .core.rules.exactly_one_of import ExactlyOneOf
from .core.rules.forbids import Forbids
from .core.rules.forbids_any import ForbidsAny
from .core.rules.mutually_exclusive import MutuallyExclusive
from .core.rules.requires import Requires
from .core.rules.requires_all import RequiresAll
from .core.rules.requires_any import RequiresAny

if TYPE_CHECKING:
    from .core.definitions.base import Definition, Value as ScalarValue
    from .core.entries.base import Entry
    from .core.rules.base import Rule

_ScalarFormatter = Callable[[object], str]


def _render_description(description: str | None) -> list[str]:
    if description is None:
        return []
    return [f"# {line}" if line else "#" for line in description.splitlines()]


def _render_metadata(member: Entry, format_scalar: _ScalarFormatter) -> list[str]:
    lines: list[str] = []
    if member.description:
        lines.extend(_render_description(member.description))

    presence = "optional" if member.optional else "required"
    metadata = f"# {presence} | {_type_name(member)}"
    if isinstance(member, Scalar) and member.default is not None:
        metadata += f" | default: {format_scalar(member.default)}"
    lines.append(metadata)
    return lines


def _type_name(member: Entry) -> str:
    if isinstance(member, Scalar):
        return field__type_name(member)
    if isinstance(member, Table):
        return "Table"
    if isinstance(member, Array):
        collection_name = "set" if member.unique else "list"
        target_name = (
            "Table" if member.entries is not None else _target_name(member.element)
        )
        return f"{target_name} {collection_name}"
    if isinstance(member, Mapping):
        target_name = (
            "Table" if member.entries is not None else _target_name(member.value)
        )
        return f"{target_name} mapping"
    return type(member).__name__


def field__type_name(field: Scalar[ScalarValue]) -> str:
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


def _target_name(target: Definition[ScalarValue] | None) -> str:
    if target is None:
        raise TypeError("scalar target is missing")
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


def _scalar_root(field: Scalar[ScalarValue]) -> tuple[type[object], str] | None:
    for field_type, name in _SCALAR_FIELD_TYPES:
        if isinstance(field, field_type):
            return field_type, name
    return None


_LITERAL_FIELD_TYPES: tuple[tuple[type[object], str], ...] = (
    (TextLiteral, "Text Literal"),
    (NumberLiteral, "Number Literal"),
    (DecimalLiteral, "Decimal Literal"),
    (OffsetDateTimeLiteral, "Offset Date Time Literal"),
    (LocalDateTimeLiteral, "Local Date Time Literal"),
    (LocalDateLiteral, "Local Date Literal"),
    (LocalTimeLiteral, "Local Time Literal"),
)


def _literal__type_name(
    field: Scalar[ScalarValue],
) -> tuple[type[object], str] | None:
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


def render(
    name: str,
    description: str,
    entries: tuple[Entry, ...],
    rules: tuple[Rule, ...],
) -> str:
    lines = [f"# {name}"]
    if description:
        lines.extend(_render_description(description))
    lines.append("")
    lines.extend(_render_entries(entries, rules).splitlines())
    return "\n".join(lines).rstrip() + "\n"


def _render_entries(
    entries: tuple[Entry, ...],
    rules: tuple[Rule, ...],
    prefix: tuple[str, ...] = (),
) -> str:
    return "\n".join(_render_entry_list(entries, rules, prefix))


def _render_entry_list(
    entries: tuple[Entry, ...], rules: tuple[Rule, ...], prefix: tuple[str, ...] = ()
) -> list[str]:
    lines: list[str] = []
    members = (
        *(member for member in entries if not _is_table_member(member)),
        *(member for member in entries if _is_table_member(member)),
    )
    for index, member in enumerate(members):
        lines.extend(_render_member(member, prefix, rules))
        if index != len(members) - 1:
            lines.append("")
    return lines


def _is_table_member(member: Entry) -> bool:
    return isinstance(member, (Table, Mapping)) or (
        isinstance(member, Array) and member.entries is not None
    )


def _render_member(
    member: Entry, prefix: tuple[str, ...], rules: tuple[Rule, ...]
) -> list[str]:
    lines = _render_metadata(member, _format_toml_scalar)
    lines.extend(_render_member_rules(member, rules))

    if isinstance(member, Scalar):
        lines.append(f"{member.name} = {_format_default(member.default)}")
        return lines

    if isinstance(member, Table):
        table_path = (*prefix, member.name)
        lines.append("")
        lines.append(f"[{'.'.join(table_path)}]")
        nested = _render_entries(member.entries, member.rules, table_path)
        if nested:
            lines.extend(nested.splitlines())
        return lines

    if isinstance(member, Array):
        if member.entries is not None:
            table_path = (*prefix, member.name)
            lines.append("")
            lines.extend(
                _render_commented_table_template(
                    member.name,
                    member.entries,
                    member.rules,
                    f"[[{'.'.join(table_path)}]]",
                    table_path,
                )
            )
        else:
            lines.append(f"# {member.name} = ")
        return lines

    if isinstance(member, Mapping):
        map_path = (*prefix, member.name)
        if member.entries is not None:
            template_path = (*map_path, "<key>")
            lines.append("")
            lines.extend(
                _render_commented_table_template(
                    member.name,
                    member.entries,
                    member.rules,
                    f"[{'.'.join(template_path)}]",
                    template_path,
                )
            )
        else:
            lines.append("")
            lines.append(f"# [{'.'.join(map_path)}]")
            lines.append("# <key> = ")
        return lines

    raise TypeError(f"unsupported member type: {type(member).__name__}")


def _render_commented_table_template(
    title: str,
    entries: tuple[Entry, ...],
    rules: tuple[Rule, ...],
    header: str,
    prefix: tuple[str, ...],
) -> list[str]:
    lines: list[str] = [f"# --- {title} table ---"]
    lines.append(f"# {header}")
    lines.append("")
    lines.extend(_comment_entries(entries, rules, prefix))
    lines.append(f"# --- end {title} table ---")
    return lines


def _comment_entries(
    entries: tuple[Entry, ...], rules: tuple[Rule, ...], prefix: tuple[str, ...] = ()
) -> list[str]:
    lines: list[str] = []
    for line in _render_entry_list(entries, rules, prefix):
        lines.append("#") if not line else lines.append(f"# {line.removeprefix('# ')}")
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
