from __future__ import annotations

from typing import Final, Generic, TypeVar

from confflow.core.types import Value

from .base import Constraint

ValueT = TypeVar(name="ValueT", bound=Value)


class Literal(Constraint[ValueT], Generic[ValueT]):
    __slots__ = ("__values",)

    NAME: Final[str] = "literal"

    def __init__(self, *values: ValueT) -> None:
        if not values:
            raise ValueError("literal constraint requires at least one value")

        self.__values: tuple[ValueT, ...] = values

    @property
    def values(self) -> tuple[ValueT, ...]:
        return self.__values

    def __call__(self, value: ValueT, /) -> None:
        if value not in self.__values:
            raise ValueError(f"value must be one of {self.__values!r}")

    def __repr__(self) -> str:
        return f"{type(self).__name__}(values={self.__values!r})"
