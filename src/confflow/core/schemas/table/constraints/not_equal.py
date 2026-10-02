from __future__ import annotations

from json import dumps
from typing import TYPE_CHECKING

from ._validation import validate_fields
from .base import Constraint

if TYPE_CHECKING:
    from collections.abc import Mapping


class NotEqual(Constraint):
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

        for index, left in enumerate(iterable=present):
            for right in present[index + 1 :]:
                if value[left] == value[right]:
                    raise ValueError(
                        f"fields {left!r} and {right!r} must have different values"
                    )

    def __str__(self) -> str:
        names = tuple(dumps(field) for field in self.fields)
        match names:
            case (left, right):
                return f"{left} != {right}"
            case _:
                fields = f"{', '.join(names[:-1])}, and {names[-1]}"
                return f"Values for {fields} must be different"

    def __repr__(self) -> str:
        return f"{type(self).__name__}(fields={self.__fields!r})"
