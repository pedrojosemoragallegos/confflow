from __future__ import annotations

from abc import ABC, abstractmethod
from typing import ClassVar, Generic, TypeVar

from confflow.core.types import Value

ValueT_contra = TypeVar(name="ValueT_contra", bound=Value, contravariant=True)


class Constraint(ABC, Generic[ValueT_contra]):
    __slots__ = ()

    NAME: ClassVar[str]

    @abstractmethod
    def __call__(self, value: ValueT_contra, /) -> None: ...
