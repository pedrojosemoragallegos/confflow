from __future__ import annotations

from typing import TYPE_CHECKING, Final, final

from typing_extensions import override

from ._validation import validate_name
from .exceptions import SchemaError
from .members.base import Entry
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


@final
class Schema:
    __slots__ = ("__description", "__members", "__name", "__rules")

    def __init__(
        self,
        name: str,
        description: str,
        /,
        *members: Entry,
        rules: Iterable[Rule] = (),
    ) -> None:
        name = validate_name(name, "schema name")
        if type(description) is not str:
            raise SchemaError("schema description must be a string")

        member_tuple = members
        if not member_tuple:
            raise SchemaError("schema must contain at least one member")
        if any(not isinstance(member, Entry) for member in member_tuple):
            raise SchemaError("schema members must be Entry instances")
        if _contains_duplicate_references(member_tuple):
            raise SchemaError("schema cannot contain the same member reference twice")
        if len({member.name for member in member_tuple}) != len(member_tuple):
            raise SchemaError("schema member names must be unique")

        rule_tuple = tuple(rules)
        if any(not isinstance(rule, Rule) for rule in rule_tuple):
            raise SchemaError("schema rules must be Rule instances")
        if _contains_duplicate_rules(rule_tuple):
            raise SchemaError("schema cannot contain duplicate rules")

        for rule in rule_tuple:
            if any(
                not _contains_reference(member_tuple, target) for target in rule.members
            ):
                raise SchemaError("rule targets must be direct members of the schema")

        _validate_direct_rule_contradictions(rule_tuple)

        self.__name: Final[str] = name
        self.__description: Final[str] = description
        self.__members: Final[tuple[Entry, ...]] = member_tuple
        self.__rules: Final[tuple[Rule, ...]] = rule_tuple

    @property
    def name(self) -> str:
        return self.__name

    @property
    def description(self) -> str:
        return self.__description

    @property
    def members(self) -> tuple[Entry, ...]:
        return self.__members

    @property
    def rules(self) -> tuple[Rule, ...]:
        return self.__rules

    @override
    def __repr__(self) -> str:
        return (
            f"Schema(name={self.__name!r}, description={self.__description!r}, "
            f"members={self.__members!r}, rules={self.__rules!r})"
        )


def _contains_reference(entries: tuple[Entry, ...], candidate: Entry) -> bool:
    return any(entry is candidate for entry in entries)


def _contains_duplicate_references(entries: tuple[Entry, ...]) -> bool:
    return any(
        left is right
        for index, left in enumerate(entries)
        for right in entries[index + 1 :]
    )


def _contains_duplicate_rules(rules: tuple[Rule, ...]) -> bool:
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
        right,
        (RequiresAny, RequiresAll, ForbidsAny),
    ):
        return left.source is right.source and _same_unordered_members(
            left.targets, right.targets
        )

    return False


def _same_unordered_members(left: tuple[Entry, ...], right: tuple[Entry, ...]) -> bool:
    return len(left) == len(right) and {id(member) for member in left} == {
        id(member) for member in right
    }


def _validate_direct_rule_contradictions(rules: tuple[Rule, ...]) -> None:
    requires = tuple(rule for rule in rules if isinstance(rule, Requires))
    forbids = tuple(rule for rule in rules if isinstance(rule, Forbids))
    if any(
        require.source is forbid.source and require.target is forbid.target
        for require in requires
        for forbid in forbids
    ):
        raise SchemaError("schema contains a direct requires/forbids contradiction")
