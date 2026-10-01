from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from .base import Constraint

if TYPE_CHECKING:
    from collections.abc import Mapping


class RequiredTogether(Constraint):
    __slots__ = ("__fields",)

    NAME: ClassVar[str] = "required_together"

    def __init__(self, *fields: str) -> None:
        if len(fields) < 2:
            raise ValueError("at least two fields are required")

        if len(set(fields)) != len(fields):
            raise ValueError("fields must be unique")

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

    def __repr__(self) -> str:
        return f"{type(self).__name__}(fields={self.__fields!r})"
