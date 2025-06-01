import copy
from abc import ABC
from typing import Generic, Iterable, Optional, TypeVar

from confflow.mixins import ReprMixin

from .constraints import Constraint

T = TypeVar("T")


class Field(ABC, Generic[T], ReprMixin):
    def __init__(
        self,
        name: str,
        description: str,
        value: Optional[T] = None,
        default_value: Optional[T] = None,
        required: bool = False,
        constraints: Optional[Iterable[Constraint[T]]] = None,
    ):
        self._name: str = name
        self._description: str = description
        self._required: bool = required
        self._constraints: set[Constraint[T]] = (
            set(constraints) if constraints else set()
        )

        if (value is None) and (default_value is None):
            raise ValueError("Either pass 'value'/'default_value' or both.")

        if default_value is not None:
            self._validate(default_value)

        self._default_value: Optional[T] = default_value

        if value is None:
            self._value: Optional[T] = self._default_value
        else:
            self._validate(value)
            self._value: Optional[T] = value

    @property
    def name(self) -> str:
        return self._name

    @property
    def default_value(self) -> Optional[T]:
        return copy.deepcopy(self._default_value)

    @default_value.setter
    def default_value(self, default_value: T) -> None:
        self._validate(value=default_value)
        self._default_value = default_value

    @property
    def value(self) -> Optional[T]:
        return copy.deepcopy(self._value)

    @value.setter
    def value(self, value: T) -> None:
        self._validate(value=value)
        self._value = value

    @property
    def description(self) -> str:
        return self._description

    @property
    def required(self) -> bool:
        return self._required

    def _validate(self, value: T) -> None:
        for constraint in self._constraints:
            constraint.validate(value)
