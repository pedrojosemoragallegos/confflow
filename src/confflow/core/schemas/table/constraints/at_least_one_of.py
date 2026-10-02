from __future__ import annotations

from json import dumps
from typing import TYPE_CHECKING

from ._validation import validate_fields
from .base import Constraint

if TYPE_CHECKING:
    from collections.abc import Mapping


class AtLeastOneOf(Constraint):
    __slots__ = ("__fields",)

    def __init__(self, *fields: str) -> None:
        validate_fields(fields, minimum=1)

        self.__fields: tuple[str, ...] = fields

    @property
    def fields(self) -> tuple[str, ...]:
        return self.__fields

    def __call__(self, value: Mapping[str, object], /) -> None:
        if not any(field in value for field in self.__fields):
            raise ValueError(f"at least one of {self.__fields!r} must be provided")

    def __str__(self) -> str:
        names = tuple(dumps(field) for field in self.fields)
        match names:
            case (name,):
                fields = name
            case (left, right):
                fields = f"{left} or {right}"
            case _:
                fields = f"{', '.join(names[:-1])}, or {names[-1]}"
        return f"At least one of {fields} must be provided"

    def __repr__(self) -> str:
        return f"{type(self).__name__}(fields={self.__fields!r})"
