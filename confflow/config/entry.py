from typing import Generic, Iterable, Optional, TypeVar

from confflow.types import Value

from ..constraints import Constraint

T = TypeVar("T", bound=Value)


class Entry(
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
        self._description: Optional[str] = description
        self._constraints: frozenset[Constraint[T]] = set(constraints or [])
        self._value: T = self._validate(value)

    @property
    def name(self) -> str:
        return self._name

    @property
    def value(self) -> T:
        return self._value

    @property
    def description(self) -> Optional[str]:
        return self._description

    @property
    def constraints(self) -> Optional[frozenset[Constraint[T]]]:
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
