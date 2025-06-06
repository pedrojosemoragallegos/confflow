import copy
from abc import ABC
from typing import Generic, Optional, Sequence, TypeVar

from confflow.core.field_values import (
    BooleanFieldValue,
    BytesFieldValue,
    FloatFieldValue,
    IntegerFieldValue,
    ListFieldValue,
    MappingFieldValue,
    SetFieldValue,
    StringFieldValue,
    TimestampFieldValue,
)
from confflow.mixins import ReprMixin

from .field_constraint import FieldConstraint

T = TypeVar("T")


class Field(ABC, Generic[T], ReprMixin):
    def __init__(
        self,
        value: T,
        *,
        name: str,
        description: Optional[str] = None,
        constraints: Optional[Sequence[FieldConstraint[T]]] = None,
    ):
        self._name: str = name
        self._description: str = description or ""
        self._constraints: frozenset[FieldConstraint[T]] = frozenset(constraints or [])

        # validate before assignment
        self._validate(value)
        self._value: T = value

    @property
    def name(self) -> str:
        return self._name

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

    def _validate(self, value: T) -> None:
        for constraint in self._constraints:
            constraint(value)


class StringField(Field[StringFieldValue]): ...


class IntegerField(Field[IntegerFieldValue]): ...


class FloatField(Field[FloatFieldValue]): ...


class BooleanField(Field[BooleanFieldValue]): ...


class TimestampField(Field[TimestampFieldValue]): ...


class BytesField(Field[BytesFieldValue]): ...


class ListField(Field[ListFieldValue]): ...


class MappingField(Field[MappingFieldValue]): ...


class SetField(Field[SetFieldValue]): ...
