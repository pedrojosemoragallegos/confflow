from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, ClassVar, Generic, TypeVar

from confflow.core.types import Value

if TYPE_CHECKING:
    from confflow.core.constraints import Constraint

ValueT = TypeVar(name="ValueT", bound=Value)


class Definition(ABC, Generic[ValueT]):
    __slots__ = ("__constraints",)

    VALUE_TYPE: ClassVar[type[Value]]

    def __init__(self, *constraints: Constraint[ValueT]) -> None:
        self.__constraints: tuple[Constraint[ValueT], ...] = constraints

    @property
    def constraints(self) -> tuple[Constraint[ValueT], ...]:
        return self.__constraints

    def validate(self, value: ValueT, /) -> None:
        # TODO: raise error if any constraint fails
        for constraint in self.__constraints:
            constraint(value)

    @abstractmethod
    def __repr__(self) -> str: ...
