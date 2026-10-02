from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from confflow.core.errors import SchemaError

from .base import Constraint

if TYPE_CHECKING:
    from collections.abc import Mapping


class Equal(Constraint):
    __slots__ = ("__fields",)

    NAME: ClassVar[str] = "equal"

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
        present: tuple[str, ...] = tuple(
            field for field in self.__fields if field in value
        )

        if len(present) < 2:
            return

        if any(value[field] != value[present[0]] for field in present[1:]):
            raise ValueError(f"fields {present!r} must have equal values")

    def __repr__(self) -> str:
        return f"{type(self).__name__}(fields={self.__fields!r})"
