from __future__ import annotations

from typing import TYPE_CHECKING, Self, final

from .configuration import Configuration
from .core.entries._scalar_builder import ScalarEntryBuilder
from .core.entries.base import Entry

if TYPE_CHECKING:
    from .core.rules.base import Rule


@final
class ConfigurationBuilder(ScalarEntryBuilder):
    __slots__ = ("__description", "__entries", "__name", "__rules")

    def __init__(
        self,
        name: str,
        description: str,
        /,
        *rules: Rule,
    ) -> None:
        self.__name = name
        self.__description = description
        self.__entries: list[Entry] = []
        self.__rules: list[Rule] = list(rules)

    def add(self, *entries: Entry) -> Self:
        self.__entries.extend(entries)
        return self

    def _store_rule(self, rule: Rule) -> Self:
        self.__rules.append(rule)
        return self

    def _entries_for_rules(self) -> tuple[Entry, ...]:
        return tuple(self.__entries)

    def build(self) -> Configuration:
        return Configuration(
            self.__name,
            self.__description,
            *self.__entries,
            rules=tuple(self.__rules),
        )
