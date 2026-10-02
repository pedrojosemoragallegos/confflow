from __future__ import annotations

from json import dumps
from typing import TYPE_CHECKING

from ._validation import validate_fields
from .base import Constraint

if TYPE_CHECKING:
    from collections.abc import Mapping


class RequiredTogether(Constraint):
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

        if not present or len(present) == len(self.__fields):
            return

        missing: tuple[str, ...] = tuple(
            field for field in self.__fields if field not in value
        )

        raise ValueError(
            f"fields {self.__fields!r} must be provided together; missing {missing!r}"
        )

    def __str__(self) -> str:
        names = tuple(dumps(field) for field in self.fields)
        match names:
            case (left, right):
                return (
                    f"When either {left} or {right} is provided, both must be provided"
                )
            case _:
                fields = f"{', '.join(names[:-1])}, or {names[-1]}"
                return (
                    f"When any of {fields} is provided, all of them must be provided"
                )

    def __repr__(self) -> str:
        return f"{type(self).__name__}(fields={self.__fields!r})"
