from __future__ import annotations

from operator import eq, ge, gt, le, lt, ne
from typing import TYPE_CHECKING, ClassVar

from confflow.core.errors import SchemaError

from .base import Constraint

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping


class Compare(Constraint):
    __slots__ = ("__left", "__operator", "__right")

    NAME: ClassVar[str] = "compare"

    OPERATORS: ClassVar[dict[str, Callable[[object, object], bool]]] = {
        "==": eq,
        "!=": ne,
        "<": lt,
        "<=": le,
        ">": gt,
        ">=": ge,
    }

    def __init__(
        self,
        left: str,
        operator: str,
        right: str,
        /,
    ) -> None:
        if left == right:
            raise SchemaError("fields must be different")

        if operator not in self.OPERATORS:
            raise SchemaError(f"unsupported comparison operator {operator!r}")

        self.__left = left
        self.__operator = operator
        self.__right = right

    @property
    def left(self) -> str:
        return self.__left

    @property
    def operator(self) -> str:
        return self.__operator

    @property
    def right(self) -> str:
        return self.__right

    @property
    def fields(self) -> tuple[str, ...]:
        return (self.__left, self.__right)

    def __call__(self, value: Mapping[str, object], /) -> None:
        if self.__left not in value or self.__right not in value:
            return

        compare = self.OPERATORS[self.__operator]

        try:
            valid = compare(
                value[self.__left],
                value[self.__right],
            )
        except TypeError as error:
            raise ValueError(
                f"fields {self.__left!r} and {self.__right!r} cannot be compared"
            ) from error

        if not valid:
            raise ValueError(
                f"field {self.__left!r} must be "
                f"{self.__operator} field {self.__right!r}"
            )

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}("
            f"left={self.__left!r}, "
            f"operator={self.__operator!r}, "
            f"right={self.__right!r})"
        )
