from __future__ import annotations

from abc import ABC, abstractmethod
from typing import ClassVar, Generic, TypeVar

from confflow.core.types import Value

ValueT_co = TypeVar(name="ValueT_co", bound=Value, covariant=True)


class Definition(ABC, Generic[ValueT_co]):
    __slots__ = ()

    VALUE_TYPE: ClassVar[type[Value]]

    @abstractmethod
    def validate(self, value: object, /) -> None: ...

    @abstractmethod
    def __repr__(self) -> str: ...
