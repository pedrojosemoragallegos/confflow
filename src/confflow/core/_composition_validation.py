from __future__ import annotations

from typing import TYPE_CHECKING

from .entries.base import Entry
from .exceptions import SchemaError
from .rules.all_or_none import AllOrNone
from .rules.at_least_one_of import AtLeastOneOf
from .rules.base import Rule
from .rules.exactly_one_of import ExactlyOneOf
from .rules.forbids import Forbids
from .rules.forbids_any import ForbidsAny
from .rules.mutually_exclusive import MutuallyExclusive
from .rules.requires import Requires
from .rules.requires_all import RequiresAll
from .rules.requires_any import RequiresAny

if TYPE_CHECKING:
    from collections.abc import Iterable


def validate_composition(
    entries: Iterable[Entry],
    rules: Iterable[Rule] | None,
    *,
    label: str,
    recursive: bool = False,
) -> tuple[tuple[Entry, ...], tuple[Rule, ...]]:
    entry_tuple = tuple(entries)
    if not entry_tuple:
        raise SchemaError(f"{label} must contain at least one entry")
    if any(not isinstance(entry, Entry) for entry in entry_tuple):
        raise SchemaError(f"{label} entries must be Entry instances")
    if contains_duplicate_references(entry_tuple):
        raise SchemaError(f"{label} cannot contain the same entry reference twice")
    if len({entry.name for entry in entry_tuple}) != len(entry_tuple):
        raise SchemaError(f"{label} entry names must be unique")

    rule_tuple = () if rules is None else tuple(rules)
    if any(not isinstance(rule, Rule) for rule in rule_tuple):
        raise SchemaError(f"{label} rules must be Rule instances")
    if contains_duplicate_rules(rule_tuple):
        raise SchemaError(f"{label} cannot contain duplicate rules")
    for rule in rule_tuple:
        if any(not contains_reference(entry_tuple, target) for target in rule.members):
            raise SchemaError(f"{label} rule targets must be direct entries")
    validate_direct_rule_contradictions(rule_tuple, label=label)

    if recursive:
        from .entries.array import Array
        from .entries.mapping import Mapping
        from .entries.table import Table

        for entry in entry_tuple:
            if isinstance(entry, Table):
                validate_composition(
                    entry.entries,
                    entry.rules,
                    label=f"table {entry.name!r}",
                    recursive=True,
                )
            elif isinstance(entry, Array) and entry.entries is not None:
                validate_composition(
                    entry.entries,
                    entry.rules,
                    label=f"array {entry.name!r} table element",
                    recursive=True,
                )
            elif isinstance(entry, Mapping) and entry.entries is not None:
                validate_composition(
                    entry.entries,
                    entry.rules,
                    label=f"map {entry.name!r} table value",
                    recursive=True,
                )

    return entry_tuple, rule_tuple


def contains_reference(entries: tuple[Entry, ...], candidate: Entry) -> bool:
    return any(entry is candidate for entry in entries)


def contains_duplicate_references(entries: tuple[Entry, ...]) -> bool:
    return any(
        left is right
        for index, left in enumerate(entries)
        for right in entries[index + 1 :]
    )


def contains_duplicate_rules(rules: tuple[Rule, ...]) -> bool:
    return any(
        _same_rule(left, right)
        for index, left in enumerate(rules)
        for right in rules[index + 1 :]
    )


def _same_rule(left: Rule, right: Rule) -> bool:
    if type(left) is not type(right):
        return False

    if isinstance(left, (MutuallyExclusive, ExactlyOneOf, AtLeastOneOf, AllOrNone)):
        return _same_unordered_members(left.members, right.members)

    if isinstance(left, (Requires, Forbids)) and isinstance(right, (Requires, Forbids)):
        return left.source is right.source and left.target is right.target

    if isinstance(left, (RequiresAny, RequiresAll, ForbidsAny)) and isinstance(
        right, (RequiresAny, RequiresAll, ForbidsAny)
    ):
        return left.source is right.source and _same_unordered_members(
            left.targets, right.targets
        )

    return False


def _same_unordered_members(left: tuple[Entry, ...], right: tuple[Entry, ...]) -> bool:
    return len(left) == len(right) and {id(member) for member in left} == {
        id(member) for member in right
    }


def validate_direct_rule_contradictions(rules: tuple[Rule, ...], *, label: str) -> None:
    requires = tuple(rule for rule in rules if isinstance(rule, Requires))
    forbids = tuple(rule for rule in rules if isinstance(rule, Forbids))
    if any(
        require.source is forbid.source and require.target is forbid.target
        for require in requires
        for forbid in forbids
    ):
        raise SchemaError(f"{label} contains a direct requires/forbids contradiction")
