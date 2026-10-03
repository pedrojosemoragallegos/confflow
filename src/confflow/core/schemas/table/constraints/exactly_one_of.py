from __future__ import annotations

from json import dumps
from typing import TYPE_CHECKING, Final

from ._validation import validate_fields
from .base import Constraint

if TYPE_CHECKING:
    from collections.abc import Mapping


class ExactlyOneOf(Constraint):
    __slots__ = ("__fields",)

    def __init__(self, *fields: str) -> None:
        validate_fields(fields)

        self.__fields: Final[tuple[str, ...]] = fields

    @property
    def fields(self) -> tuple[str, ...]:
        return self.__fields

    def __call__(self, value: Mapping[str, object], /) -> None:
        if sum(field in value for field in self.__fields) != 1:
            raise ValueError(f"exactly one of {self.__fields!r} must be provided")

    def __str__(self) -> str:
        names = tuple(dumps(field) for field in self.fields)
        match names:
            case (left, right):
                return f"Either {left} or {right}, but not both, must be provided"
            case _:
                fields = f"{', '.join(names[:-1])}, or {names[-1]}"
                return f"Exactly one of {fields} must be provided"

    def __repr__(self) -> str:
        return f"{type(self).__name__}(fields={self.__fields!r})"
