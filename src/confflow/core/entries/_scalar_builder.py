from __future__ import annotations

from typing import TYPE_CHECKING, Any, Self

from ..exceptions import SchemaError
from ..rules.all_or_none import AllOrNone as AllOrNoneRule
from ..rules.at_least_one_of import AtLeastOneOf as AtLeastOneOfRule
from ..rules.exactly_one_of import ExactlyOneOf as ExactlyOneOfRule
from ..rules.forbids import Forbids as ForbidsRule
from ..rules.forbids_any import ForbidsAny as ForbidsAnyRule
from ..rules.mutually_exclusive import MutuallyExclusive as MutuallyExclusiveRule
from ..rules.requires import Requires as RequiresRule
from ..rules.requires_all import RequiresAll as RequiresAllRule
from ..rules.requires_any import RequiresAny as RequiresAnyRule
from .array import Array
from .mapping import Mapping
from .scalars.boolean import Boolean
from .scalars.decimal import Decimal
from .scalars.literals.decimal import DecimalLiteral
from .scalars.literals.local_date import LocalDateLiteral
from .scalars.literals.local_date_time import LocalDateTimeLiteral
from .scalars.literals.local_time import LocalTimeLiteral
from .scalars.literals.number import NumberLiteral
from .scalars.literals.offset_date_time import OffsetDateTimeLiteral
from .scalars.literals.text import TextLiteral
from .scalars.local_date import LocalDate
from .scalars.local_date_time import LocalDateTime
from .scalars.local_time import LocalTime
from .scalars.number import Number
from .scalars.offset_date_time import OffsetDateTime
from .scalars.text import Text

if TYPE_CHECKING:
    from collections.abc import Iterable
    from datetime import date, datetime, time

    from ..definitions.base import Definition, Value as DefinitionValue
    from ..rules.base import Rule
    from .base import Entry
    from .scalars.base import Scalar


class ScalarEntryBuilder:
    __slots__ = ()

    def add(self, *entries: Entry) -> Self:
        raise NotImplementedError

    def _store_rule(self, rule: Rule) -> Self:
        raise NotImplementedError

    def _entries_for_rules(self) -> tuple[Entry, ...]:
        raise NotImplementedError

    def _resolve_entries(self, names: tuple[str, ...]) -> tuple[Entry, ...]:
        entries = self._entries_for_rules()
        resolved: list[Entry] = []
        for name in names:
            matches = tuple(entry for entry in entries if entry.name == name)
            if len(matches) != 1:
                raise SchemaError(f"builder has no unique entry named {name!r}")
            resolved.append(matches[0])
        return tuple(resolved)

    def MutuallyExclusive(self, *members: str) -> Self:
        return self._store_rule(MutuallyExclusiveRule(*self._resolve_entries(members)))

    def ExactlyOneOf(self, *members: str) -> Self:
        return self._store_rule(ExactlyOneOfRule(*self._resolve_entries(members)))

    def AtLeastOneOf(self, *members: str) -> Self:
        return self._store_rule(AtLeastOneOfRule(*self._resolve_entries(members)))

    def AllOrNone(self, *members: str) -> Self:
        return self._store_rule(AllOrNoneRule(*self._resolve_entries(members)))

    def Requires(self, *, source: str, target: str) -> Self:
        source_entry, target_entry = self._resolve_entries((source, target))
        return self._store_rule(RequiresRule(source=source_entry, target=target_entry))

    def RequiresAny(self, *targets: str, source: str) -> Self:
        source_entry, *target_entries = self._resolve_entries((source, *targets))
        return self._store_rule(RequiresAnyRule(source_entry, *target_entries))

    def RequiresAll(self, *targets: str, source: str) -> Self:
        source_entry, *target_entries = self._resolve_entries((source, *targets))
        return self._store_rule(RequiresAllRule(source_entry, *target_entries))

    def Forbids(self, *, source: str, target: str) -> Self:
        source_entry, target_entry = self._resolve_entries((source, target))
        return self._store_rule(ForbidsRule(source=source_entry, target=target_entry))

    def ForbidsAny(self, *targets: str, source: str) -> Self:
        source_entry, *target_entries = self._resolve_entries((source, *targets))
        return self._store_rule(ForbidsAnyRule(source_entry, *target_entries))

    def Text(
        self,
        name: str,
        description: str | None = None,
        /,
        *,
        optional: bool = False,
        default: str | None = None,
        minimum: int | None = None,
        maximum: int | None = None,
        length: int | None = None,
        pattern: str | None = None,
    ) -> Self:
        self.add(
            Text(
                name,
                description,
                optional=optional,
                default=default,
                minimum=minimum,
                maximum=maximum,
                length=length,
                pattern=pattern,
            )
        )
        return self

    def Number(
        self,
        name: str,
        description: str | None = None,
        /,
        *,
        optional: bool = False,
        default: int | None = None,
        minimum: int | None = None,
        maximum: int | None = None,
    ) -> Self:
        self.add(
            Number(
                name,
                description,
                optional=optional,
                default=default,
                minimum=minimum,
                maximum=maximum,
            )
        )
        return self

    def Decimal(
        self,
        name: str,
        description: str | None = None,
        /,
        *,
        optional: bool = False,
        default: float | None = None,
        minimum: float | None = None,
        maximum: float | None = None,
    ) -> Self:
        self.add(
            Decimal(
                name,
                description,
                optional=optional,
                default=default,
                minimum=minimum,
                maximum=maximum,
            )
        )
        return self

    def Boolean(
        self,
        name: str,
        description: str | None = None,
        /,
        *,
        optional: bool = False,
        default: bool | None = None,
    ) -> Self:
        self.add(Boolean(name, description, optional=optional, default=default))
        return self

    def LocalDate(
        self,
        name: str,
        description: str | None = None,
        /,
        *,
        optional: bool = False,
        default: date | None = None,
        minimum: date | None = None,
        maximum: date | None = None,
    ) -> Self:
        self.add(
            LocalDate(
                name,
                description,
                optional=optional,
                default=default,
                minimum=minimum,
                maximum=maximum,
            )
        )
        return self

    def LocalTime(
        self,
        name: str,
        description: str | None = None,
        /,
        *,
        optional: bool = False,
        default: time | None = None,
        minimum: time | None = None,
        maximum: time | None = None,
    ) -> Self:
        self.add(
            LocalTime(
                name,
                description,
                optional=optional,
                default=default,
                minimum=minimum,
                maximum=maximum,
            )
        )
        return self

    def LocalDateTime(
        self,
        name: str,
        description: str | None = None,
        /,
        *,
        optional: bool = False,
        default: datetime | None = None,
        minimum: datetime | None = None,
        maximum: datetime | None = None,
    ) -> Self:
        self.add(
            LocalDateTime(
                name,
                description,
                optional=optional,
                default=default,
                minimum=minimum,
                maximum=maximum,
            )
        )
        return self

    def OffsetDateTime(
        self,
        name: str,
        description: str | None = None,
        /,
        *,
        optional: bool = False,
        default: datetime | None = None,
        minimum: datetime | None = None,
        maximum: datetime | None = None,
    ) -> Self:
        self.add(
            OffsetDateTime(
                name,
                description,
                optional=optional,
                default=default,
                minimum=minimum,
                maximum=maximum,
            )
        )
        return self

    def Array(
        self,
        name: str,
        description: str | None = None,
        /,
        *,
        optional: bool = False,
        element: Definition[DefinitionValue] | Scalar[Any] | None = None,
        entries: Iterable[Entry] | None = None,
        rules: Iterable[Rule] | None = None,
        minimum_length: int | None = None,
        maximum_length: int | None = None,
        unique: bool = False,
    ) -> Self:
        self.add(
            Array(
                name,
                description,
                optional=optional,
                element=element,
                entries=entries,
                rules=rules,
                minimum_length=minimum_length,
                maximum_length=maximum_length,
                unique=unique,
            )
        )
        return self

    def Mapping(
        self,
        name: str,
        description: str | None = None,
        /,
        *,
        optional: bool = False,
        value: Definition[DefinitionValue] | Scalar[Any] | None = None,
        entries: Iterable[Entry] | None = None,
        rules: Iterable[Rule] | None = None,
        key: Definition[str] | Scalar[Any] | None = None,
        minimum_entries: int | None = None,
        maximum_entries: int | None = None,
    ) -> Self:
        self.add(
            Mapping(
                name,
                description,
                optional=optional,
                value=value,
                entries=entries,
                rules=rules,
                key=key,
                minimum_entries=minimum_entries,
                maximum_entries=maximum_entries,
            )
        )
        return self

    def TextLiteral(
        self,
        name: str,
        description: str | None = None,
        /,
        *values: str,
        optional: bool = False,
        default: str | None = None,
    ) -> Self:
        self.add(
            TextLiteral(name, description, *values, optional=optional, default=default)
        )
        return self

    def NumberLiteral(
        self,
        name: str,
        description: str | None = None,
        /,
        *values: int,
        optional: bool = False,
        default: int | None = None,
    ) -> Self:
        self.add(
            NumberLiteral(
                name, description, *values, optional=optional, default=default
            )
        )
        return self

    def DecimalLiteral(
        self,
        name: str,
        description: str | None = None,
        /,
        *values: float,
        optional: bool = False,
        default: float | None = None,
    ) -> Self:
        self.add(
            DecimalLiteral(
                name, description, *values, optional=optional, default=default
            )
        )
        return self

    def LocalDateLiteral(
        self,
        name: str,
        description: str | None = None,
        /,
        *values: date,
        optional: bool = False,
        default: date | None = None,
    ) -> Self:
        self.add(
            LocalDateLiteral(
                name, description, *values, optional=optional, default=default
            )
        )
        return self

    def LocalTimeLiteral(
        self,
        name: str,
        description: str | None = None,
        /,
        *values: time,
        optional: bool = False,
        default: time | None = None,
    ) -> Self:
        self.add(
            LocalTimeLiteral(
                name, description, *values, optional=optional, default=default
            )
        )
        return self

    def LocalDateTimeLiteral(
        self,
        name: str,
        description: str | None = None,
        /,
        *values: datetime,
        optional: bool = False,
        default: datetime | None = None,
    ) -> Self:
        self.add(
            LocalDateTimeLiteral(
                name, description, *values, optional=optional, default=default
            )
        )
        return self

    def OffsetDateTimeLiteral(
        self,
        name: str,
        description: str | None = None,
        /,
        *values: datetime,
        optional: bool = False,
        default: datetime | None = None,
    ) -> Self:
        self.add(
            OffsetDateTimeLiteral(
                name, description, *values, optional=optional, default=default
            )
        )
        return self
