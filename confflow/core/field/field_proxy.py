from types import MappingProxyType
from typing import Generic, TypeVar

from ..types import FieldValue
from .field import BaseField

T = TypeVar("T", bound=FieldValue)


class FieldProxy(Generic[T]):
    def __init__(self, field: BaseField[T]):
        self._field = field

    @property
    def name(self) -> str:
        return self._field.name

    @property
    def description(self) -> str:
        return self._field.description

    @property
    def value(self) -> T:
        value: T = self._field.value

        if isinstance(value, dict):
            return MappingProxyType(value)
        elif isinstance(value, list):
            return tuple(value)
        elif isinstance(value, set):
            return frozenset(value)
        else:
            return value  # primitives or already immutable
