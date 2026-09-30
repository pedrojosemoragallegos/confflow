from __future__ import annotations

from typing import TYPE_CHECKING, final

from typing_extensions import override

from .._composition_validation import validate_composition
from .._validators import validate_mapping
from ._scalar_builder import ScalarEntryBuilder
from .base import Entry

if TYPE_CHECKING:
    from collections.abc import Iterable

    from ..rules.base import Rule


@final
class Table(Entry, ScalarEntryBuilder):
    __slots__ = ("__entries", "__rules")

    def __init__(
        self,
        name: str,
        description: str | None = None,
        /,
        *,
        optional: bool = False,
        entries: Iterable[Entry] = (),
        rules: Iterable[Rule] | None = None,
    ) -> None:
        super().__init__(name, description, optional=optional)

        entry_tuple = tuple(entries)
        if entry_tuple:
            validate_composition(entry_tuple, None, label="table")
        self.__entries: list[Entry] = list(entry_tuple)
        self.__rules: list[Rule] = [] if rules is None else list(rules)

    def add(self, *entries: Entry) -> Table:
        if entries:
            entry_tuple, _ = validate_composition(
                (*self.__entries, *entries), None, label="table"
            )
            self.__entries = list(entry_tuple)
        return self

    def _store_rule(self, rule: Rule) -> Table:
        self.__rules.append(rule)
        return self

    def _entries_for_rules(self) -> tuple[Entry, ...]:
        return self.entries

    @property
    def entries(self) -> tuple[Entry, ...]:
        return tuple(self.__entries)

    @property
    def rules(self) -> tuple[Rule, ...]:
        return tuple(self.__rules)

    def validate(self, value: object) -> None:
        entries, rules = validate_composition(
            self.__entries, self.__rules, label="table", recursive=True
        )
        validate_mapping(entries, rules, value)

    @override
    def __repr__(self) -> str:
        return (
            f"Table(name={self.name!r}, description={self.description!r}, "
            f"optional={self.optional!r}, entries={self.__entries!r}, "
            f"rules={self.__rules!r})"
        )
