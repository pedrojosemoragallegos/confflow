from abc import ABC
from typing import Generic, Iterable, Optional, TypeVar

from confflow.mixins import ReprMixin
from confflow.types import Value, View
from confflow.utils import freeze

from .constraint.constraint import Constraint

T = TypeVar("T", bound=Value)


class Field(ABC, Generic[T], ReprMixin):
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

        # validate before assignment
        self._validate(value)
        self._value: T = value

    @property
    def name(self) -> str:
        return self._name

    @property
    def value(self) -> View:
        return freeze(self._value)

    @value.setter
    def value(self, value: T) -> None:
        self._validate(value=value)
        self._value = value

    @property
    def description(self) -> str:
        return self._description

    def _validate(self, value: T) -> None:
        for constraint in self._constraints:
            constraint(value)
