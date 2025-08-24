from abc import ABC
from typing import Generic, Iterable, Optional, TypeVar

from confflow.types import Value

from ..constraint import Constraint

T = TypeVar("T", bound=Value)


class Entry(
    ABC,
    Generic[T],
):
    def __init__(
        self,
        value: T,
        *,
        name: str,
        description: Optional[str] = None,
        constraints: Optional[Iterable[Constraint[T]]] = None,
    ):
        self._name: str = name
        self._description: str = description or ""
        self._constraints: set[Constraint[T]] = set(constraints or [])

        self._value: T = self._validate(value)

    @property
    def name(self) -> str:
        return self._name

    @property
    def value(self) -> T:
        return self._value

    @property
    def description(self) -> str:
        return self._description

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
