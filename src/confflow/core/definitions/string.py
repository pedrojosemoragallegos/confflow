from __future__ import annotations

from re import compile as compile_pattern, error as regex_error, fullmatch
from typing import ClassVar, Final

from typing_extensions import override

from ._validators import (
    validate_integer_bounds,
    validate_non_negative_integer,
)
from .base import Definition
from .exceptions import DefinitionError


class String(Definition[str]):
    __slots__ = ("__length", "__maximum", "__minimum", "__pattern")

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
            validate_non_negative_integer("minimum length", value=minimum)

        if maximum is not None:
            validate_non_negative_integer("maximum length", value=maximum)

        if length is not None:
            validate_non_negative_integer("length", value=length)

        if minimum is not None and maximum is not None:
            validate_integer_bounds("string length", minimum=minimum, maximum=maximum)

        if length is not None and (minimum is not None or maximum is not None):
            raise DefinitionError("length cannot be combined with minimum or maximum")

        if pattern is not None:
            try:
                compile_pattern(pattern)
            except regex_error as error:
                raise DefinitionError(
                    "string pattern must be a valid regular expression"
                ) from error

        self.__minimum: Final[int | None] = minimum
        self.__maximum: Final[int | None] = maximum
        self.__length: Final[int | None] = length
        self.__pattern: Final[str | None] = pattern

    @override
    def validate(self, value: object, /) -> None:
        if type(value) is not str:
            raise DefinitionError("expected string")

        if (minimum := self.__minimum) is not None and len(value) < minimum:
            raise DefinitionError("string is shorter than the minimum length")

        if (maximum := self.__maximum) is not None and len(value) > maximum:
            raise DefinitionError("string exceeds the maximum length")

        if (length := self.__length) is not None and len(value) != length:
            raise DefinitionError("string does not have the required exact length")

        if (pattern := self.__pattern) is not None and fullmatch(
            pattern=pattern, string=value
        ) is None:
            raise DefinitionError("string does not match the required pattern")

    @override
    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}("
            f"minimum={self.__minimum!r}, maximum={self.__maximum!r}, "
            f"length={self.__length!r}, pattern={self.__pattern!r})"
        )
