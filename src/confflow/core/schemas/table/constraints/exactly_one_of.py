from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from confflow.core.errors import SchemaError

from .base import Constraint

if TYPE_CHECKING:
    from collections.abc import Mapping


class ExactlyOneOf(Constraint):
    __slots__ = ("__fields",)

    NAME: ClassVar[str] = "exactly_one_of"

    def __init__(self, *fields: str) -> None:
        if len(fields) < 2:
            raise SchemaError("at least two fields are required")

        if len(set(fields)) != len(fields):
            raise SchemaError("fields must be unique")

        self.__fields: tuple[str, ...] = fields

    @property
    def fields(self) -> tuple[str, ...]:
        return self.__fields

    def __call__(self, value: Mapping[str, object], /) -> None:
        if sum(field in value for field in self.__fields) != 1:
            raise ValueError(f"exactly one of {self.__fields!r} must be provided")

    def __repr__(self) -> str:
        return f"{type(self).__name__}(fields={self.__fields!r})"
