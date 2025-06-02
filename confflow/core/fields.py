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
        name: str,
        description: Optional[str] = None,
        value: Optional[T] = None,
        default_value: Optional[T] = None,
        constraints: Optional[Sequence[FieldConstraint["Field[T]"]]] = None,
    ):
        self._name: str = name
        self._description: str = description or ""
        self._constraints: frozenset[FieldConstraint["Field[T]"]] = (
            frozenset(constraints) if constraints else frozenset()
        )

        if (value is None) and (default_value is None):
            raise ValueError("Either pass 'value'/'default_value' or both.")

        # if default_value is not None:
        #     self._validate(default_value)

        self._default_value: Optional[T] = default_value

        if value is None:
            self._value: Optional[T] = self._default_value
        else:
            # self._validate(value)
            self._value: Optional[T] = value

    @property
    def name(self) -> str:
        return self._name

    @property
    def default_value(self) -> Optional[T]:
        return copy.deepcopy(self._default_value)

    @default_value.setter
    def default_value(self, default_value: T) -> None:
        # self._validate(value=default_value)
        self._default_value = default_value

    @property
    def value(self) -> T:
        if not self._value:
            raise  # TODO correct it

        return copy.deepcopy(self._value)

    @value.setter
    def value(self, value: T) -> None:
        # self._validate(value=value)
        self._value = value

    @property
    def description(self) -> str:
        return self._description

    # def _validate(self, value: T) -> None:
    #     for constraint in self._constraints:
    #         constraint(value)


class StringField(Field[StringFieldValue]): ...


class IntegerField(Field[IntegerFieldValue]): ...


class FloatField(Field[FloatFieldValue]): ...


class BooleanField(Field[BooleanFieldValue]): ...


class TimestampField(Field[TimestampFieldValue]): ...


class BytesField(Field[BytesFieldValue]): ...


class ListField(Field[ListFieldValue]): ...


class MappingField(Field[MappingFieldValue]): ...


class SetField(Field[SetFieldValue]): ...
