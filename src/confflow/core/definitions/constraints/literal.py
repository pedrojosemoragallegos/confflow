from __future__ import annotations

from typing import Generic, TypeVar

import tomlkit

from confflow.core.types import Value

from .base import Constraint

ValueT = TypeVar(name="ValueT", bound=Value)


class Literal(Constraint[ValueT], Generic[ValueT]):
    __slots__ = ("__values",)

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

    def __str__(self) -> str:
        values: tuple[str, ...] = tuple(
            tomlkit.dumps({"value": value}).rstrip("\n").partition(" = ")[2]
            for value in self.values
        )

        match values:
            case (value,):
                return f"Value must be {value}"
            case (left, right):
                choices = f"{left} or {right}"
            case _:
                choices = f"{', '.join(values[:-1])}, or {values[-1]}"
        return f"Value must be one of {choices}"
