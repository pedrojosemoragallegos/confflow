from __future__ import annotations

from json import dumps
from typing import TYPE_CHECKING

from ._validation import validate_fields
from .base import Constraint

if TYPE_CHECKING:
    from collections.abc import Mapping


class Equal(Constraint):
    __slots__ = ("__fields",)

    def __init__(self, *fields: str) -> None:
        validate_fields(fields)

        self.__fields: tuple[str, ...] = fields

    @property
    def fields(self) -> tuple[str, ...]:
        return self.__fields

    def __call__(self, value: Mapping[str, object], /) -> None:
        present: tuple[str, ...] = tuple(
            field for field in self.__fields if field in value
        )

        if len(present) <= 1:
            return

        if any(value[field] != value[present[0]] for field in present[1:]):
            raise ValueError(f"fields {present!r} must have equal values")

    def __str__(self) -> str:
        names = tuple(dumps(field) for field in self.fields)
        match names:
            case (left, right):
                fields = f"{left} and {right}"
            case _:
                fields = f"{', '.join(names[:-1])}, and {names[-1]}"
        return f"{fields} must have equal values when provided"

    def __repr__(self) -> str:
        return f"{type(self).__name__}(fields={self.__fields!r})"
