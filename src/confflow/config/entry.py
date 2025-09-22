from __future__ import annotations

import typing
from datetime import datetime

if typing.TYPE_CHECKING:
    from collections.abc import Iterable

    from confflow.constraints import Constraint

T = typing.TypeVar(
    "T",
    str,
    int,
    float,
    bool,
    datetime,
    bytes,
    list[str],
    list[int],
    list[float],
    list[bool],
    list[datetime],
    list[bytes],
)


class Entry(typing.Generic[T]):
    def __init__(
        self,
        value: T,
        *,
        name: str,
        description: str | None = None,
        constraints: Iterable[Constraint[T]] | None = None,
    ) -> None:
        self._name: str = name
        self._description: str | None = description
        self._constraints: typing.Final[set[Constraint[T]]] = set(constraints or [])
        self._value: T = self._validate(value)

    @property
    def name(self) -> str:
        return self._name

    @property
    def value(self) -> T:
        return self._value

    @property
    def description(self) -> str | None:
        return self._description

    @property
    def constraints(self) -> set[Constraint[T]]:
        return self._constraints

    def _validate(self, value: T) -> T:
        for constraint in self._constraints:
            constraint(value)

        return value

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"name='{self.name}', "
            f"value={self.value!r}, "
            f"description={self.description!r}, "
            f"constraints={list(self._constraints) if self._constraints else []!r})"
        )
