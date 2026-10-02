from __future__ import annotations

from json import dumps
from typing import TYPE_CHECKING

from confflow.core.errors import SchemaError

from ._validation import validate_names
from .base import Constraint

if TYPE_CHECKING:
    from collections.abc import Mapping


class Forbids(Constraint):
    __slots__ = ("__field", "__forbidden")

    def __init__(self, field: str, /, *forbidden: str) -> None:
        if not forbidden:
            raise SchemaError("at least one forbidden field is needed")
        validate_names((field, *forbidden))
        if field in forbidden:
            raise SchemaError("field cannot forbid itself")
        if len(set(forbidden)) != len(forbidden):
            raise SchemaError("forbidden fields must be unique")
        self.__field: str = field
        self.__forbidden: tuple[str, ...] = forbidden

    @property
    def field(self) -> str:
        return self.__field

    @property
    def forbidden(self) -> tuple[str, ...]:
        return self.__forbidden

    @property
    def fields(self) -> tuple[str, ...]:
        return (self.__field, *self.__forbidden)

    def __call__(self, value: Mapping[str, object], /) -> None:
        if self.__field not in value:
            return
        present = tuple(field for field in self.__forbidden if field in value)
        if present:
            raise ValueError(f"field {self.__field!r} forbids fields {present!r}")

    def __str__(self) -> str:
        names = tuple(dumps(field) for field in self.forbidden)
        match names:
            case (name,):
                fields = name
            case (left, right):
                fields = f"{left} and {right}"
            case _:
                fields = f"{', '.join(names[:-1])}, and {names[-1]}"
        return f"{fields} must be omitted when {dumps(self.field)} is provided"

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}("
            f"field={self.__field!r}, "
            f"forbidden={self.__forbidden!r})"
        )
