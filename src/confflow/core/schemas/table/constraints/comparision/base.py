from __future__ import annotations

from confflow.core.errors import SchemaError
from confflow.core.schemas.table.constraints._validation import validate_names
from confflow.core.schemas.table.constraints.base import Constraint


class Comparision(Constraint):
    __slots__ = ("__left", "__right")

    def __init__(self, left: str, right: str, /) -> None:
        validate_names((left, right))
        if left == right:
            raise SchemaError("fields must be different")

        self.__left: str = left
        self.__right: str = right

    @property
    def left(self) -> str:
        return self.__left

    @property
    def right(self) -> str:
        return self.__right

    @property
    def fields(self) -> tuple[str, ...]:
        return (self.__left, self.__right)

    def __repr__(self) -> str:
        return f"{type(self).__name__}(left={self.__left!r}, right={self.__right!r})"
