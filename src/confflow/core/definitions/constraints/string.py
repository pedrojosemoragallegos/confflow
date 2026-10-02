from __future__ import annotations

from re import Pattern as RegexPattern, compile as compile_pattern, error as regex_error
from typing import Final

from typing_extensions import override

from confflow.core.errors import SchemaError

from .base import Constraint


class String(Constraint[str]):
    __slots__ = ()


class Length(String):
    __slots__ = ("__length", "__maximum", "__minimum")

    NAME: Final[str] = "length"

    def __init__(
        self,
        *,
        minimum: int | None = None,
        maximum: int | None = None,
        length: int | None = None,
    ) -> None:
        for label, value in (
            ("minimum length", minimum),
            ("maximum length", maximum),
            ("length", length),
        ):
            if value is not None and (type(value) is not int or value < 0):
                raise SchemaError(f"{label} must be a non-negative integer")

        if minimum is not None and maximum is not None and minimum > maximum:
            raise SchemaError("string length minimum cannot exceed maximum")

        if length is not None and (minimum is not None or maximum is not None):
            raise SchemaError("length cannot be combined with minimum or maximum")

        self.__minimum: Final[int | None] = minimum
        self.__maximum: Final[int | None] = maximum
        self.__length: Final[int | None] = length

    @property
    def minimum(self) -> int | None:
        return self.__minimum

    @property
    def maximum(self) -> int | None:
        return self.__maximum

    @property
    def length(self) -> int | None:
        return self.__length

    @override
    def __call__(self, value: str, /) -> None:
        if (minimum := self.__minimum) is not None and len(value) < minimum:
            raise ValueError("string is shorter than the minimum length")

        if (maximum := self.__maximum) is not None and len(value) > maximum:
            raise ValueError("string exceeds the maximum length")

        if (length := self.__length) is not None and len(value) != length:
            raise ValueError("string does not have the required exact length")


class Pattern(String):
    __slots__ = ("__compiled", "__flags", "__pattern")

    NAME: Final[str] = "pattern"

    def __init__(self, pattern: str | RegexPattern[str]) -> None:
        if isinstance(pattern, RegexPattern):
            if not isinstance(pattern.pattern, str):
                raise SchemaError("string pattern must be a text regular expression")

            compiled: Final[RegexPattern[str]] = pattern
            pattern_text: Final[str] = pattern.pattern
        elif isinstance(pattern, str):
            try:
                compiled = compile_pattern(pattern)
            except regex_error as error:
                raise SchemaError(
                    "string pattern must be a valid regular expression"
                ) from error

            pattern_text: str = pattern
        else:
            raise SchemaError(
                "pattern must be a string or compiled text regular expression"
            )

        self.__compiled: Final[RegexPattern[str]] = compiled
        self.__pattern: Final[str] = pattern_text
        self.__flags: Final[int] = compiled.flags

    @property
    def pattern(self) -> str:
        return self.__pattern

    @property
    def flags(self) -> int:
        return self.__flags

    @override
    def __call__(self, value: str, /) -> None:
        if self.__compiled.fullmatch(string=value) is None:
            raise ValueError("string does not match the required pattern")
