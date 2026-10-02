from __future__ import annotations

from json import dumps
from typing import TYPE_CHECKING

from confflow.core.errors import SchemaError

from ._validation import validate_names
from .base import Constraint

if TYPE_CHECKING:
    from collections.abc import Mapping


class Requires(Constraint):
    __slots__ = ("__field", "__required")

    def __init__(self, field: str, /, *required: str) -> None:
        if not required:
            raise SchemaError("at least one required field is needed")

        validate_names((field, *required))
        if field in required:
            raise SchemaError("field cannot require itself")

        if len(set(required)) != len(required):
            raise SchemaError("required fields must be unique")

        self.__field: str = field
        self.__required: tuple[str, ...] = required

    @property
    def field(self) -> str:
        return self.__field

    @property
    def required(self) -> tuple[str, ...]:
        return self.__required

    @property
    def fields(self) -> tuple[str, ...]:
        return (self.__field, *self.__required)

    def __call__(self, value: Mapping[str, object], /) -> None:
        if self.__field not in value:
            return

        missing: tuple[str, ...] = tuple(
            field for field in self.__required if field not in value
        )

        if missing:
            raise ValueError(f"field {self.__field!r} requires fields {missing!r}")

    def __str__(self) -> str:
        names = tuple(dumps(field) for field in self.required)
        match names:
            case (name,):
                fields = name
            case (left, right):
                fields = f"{left} and {right}"
            case _:
                fields = f"{', '.join(names[:-1])}, and {names[-1]}"
        return f"{dumps(self.field)} requires {fields} to be provided"

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}("
            f"field={self.__field!r}, "
            f"required={self.__required!r})"
        )
