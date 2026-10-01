from __future__ import annotations

from re import compile as compile_pattern, error as regex_error, fullmatch
from typing import Final

from typing_extensions import override

from confflow.core.constraints import Constraint


class Length(Constraint[str]):
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
                raise ValueError(f"{label} must be a non-negative integer")

        if minimum is not None and maximum is not None and minimum > maximum:
            raise ValueError("string length minimum cannot exceed maximum")

        if length is not None and (minimum is not None or maximum is not None):
            # TODO: raise own exception
            raise ValueError("length cannot be combined with minimum or maximum")

        self.__minimum: Final[int | None] = minimum
        self.__maximum: Final[int | None] = maximum
        self.__length: Final[int | None] = length

    @override
    def __call__(self, value: str, /) -> None:
        if (minimum := self.__minimum) is not None and len(value) < minimum:
            # TODO: raise own exception
            raise RuntimeError("string is shorter than the minimum length")

        if (maximum := self.__maximum) is not None and len(value) > maximum:
            # TODO: raise own exception
            raise RuntimeError("string exceeds the maximum length")

        if (length := self.__length) is not None and len(value) != length:
            # TODO: raise own exception
            raise RuntimeError("string does not have the required exact length")


class Pattern(Constraint[str]):
    __slots__ = ("__pattern",)

    NAME: Final[str] = "pattern"

    def __init__(self, pattern: str) -> None:  # TODO: pattern or regex object
        try:
            compile_pattern(pattern)
        except regex_error as error:
            # TODO: raise own exception
            raise ValueError(
                "string pattern must be a valid regular expression"
            ) from error

        self.__pattern: Final[str] = pattern

    @override
    def __call__(self, value: str, /) -> None:
        if fullmatch(pattern=self.__pattern, string=value) is None:
            # TODO: raise own exception
            raise RuntimeError("string does not match the required pattern")
