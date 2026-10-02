from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from confflow.core.types import Value

ValueT_contra = TypeVar(name="ValueT_contra", bound=Value, contravariant=True)


class Constraint(ABC, Generic[ValueT_contra]):
    __slots__ = ()

    def __str__(self) -> str:
        return ""

    @abstractmethod
    def __call__(self, value: ValueT_contra, /) -> None: ...
