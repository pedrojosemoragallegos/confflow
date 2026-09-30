from __future__ import annotations

from re import compile as compile_pattern, error as regex_error, fullmatch
from typing import ClassVar, Final

from typing_extensions import override

from ..exceptions import SchemaError
from ._validators import (
    validate_integer_bounds,
    validate_non_negative_integer,
)
from .base import Definition
from .exceptions import DefinitionError


class Text(Definition[str]):
    __slots__ = (
        "__length",
        "__maximum",
        "__minimum",
        "__pattern",
    )

    VALUE_TYPE: ClassVar[type[str]] = str

    @override
    def __init__(
        self,
        *,
        minimum: int | None = None,
        maximum: int | None = None,
        length: int | None = None,
        pattern: str | None = None,
    ) -> None:
        if minimum is not None:
            validate_non_negative_integer(value=minimum, label="minimum length")

        if maximum is not None:
            validate_non_negative_integer(value=maximum, label="maximum length")

        if length is not None:
            validate_non_negative_integer(value=length, label="length")

        if minimum is not None and maximum is not None:
            validate_integer_bounds(
                minimum=minimum,
                maximum=maximum,
                label="text length",
            )

        if length is not None and (minimum is not None or maximum is not None):
            raise SchemaError("length cannot be combined with minimum or maximum")

        if pattern is not None:
            try:
                compile_pattern(pattern)
            except regex_error as error:
                raise SchemaError(
                    "text pattern must be a valid regular expression"
                ) from error

        self.__minimum: Final[int | None] = minimum
        self.__maximum: Final[int | None] = maximum
        self.__length: Final[int | None] = length
        self.__pattern: Final[str | None] = pattern

    @override
    def validate(self, value: object) -> None:
        if type(value) is not str:
            raise DefinitionError("expected text")

        if (minimum := self.__minimum) is not None and len(value) < minimum:
            raise DefinitionError("text is shorter than the minimum length")

        if (maximum := self.__maximum) is not None and len(value) > maximum:
            raise DefinitionError("text exceeds the maximum length")

        if (length := self.__length) is not None and len(value) != length:
            raise DefinitionError("text does not have the required exact length")

        if (pattern := self.__pattern) is not None and fullmatch(
            pattern,
            string=value,
        ) is None:
            raise DefinitionError("text does not match the required pattern")

    @override
    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}("
            f"minimum={self.__minimum!r}, maximum={self.__maximum!r}, "
            f"length={self.__length!r}, pattern={self.__pattern!r})"
        )
