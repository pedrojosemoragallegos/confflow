from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date, datetime, time
from typing import Generic, TypeAlias, TypeVar

TomlScalar: TypeAlias = str | int | float | bool | datetime | date | time
TomlScalarT_co = TypeVar("TomlScalarT_co", bound=TomlScalar, covariant=True)


class Definition(ABC, Generic[TomlScalarT_co]):
    __slots__ = ()

    @property
    @abstractmethod
    def value_type(self) -> type[TomlScalar]:
        raise NotImplementedError

    @abstractmethod
    def validate(self, value: object, path: tuple[str | int, ...]) -> None:
        raise NotImplementedError

    @abstractmethod
    def __repr__(self) -> str:
        raise NotImplementedError
