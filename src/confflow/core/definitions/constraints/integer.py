from __future__ import annotations

from typing import Final

import tomlkit

from .base import Constraint


class Integer(Constraint[int]):
    __slots__ = ()


class Range(Integer):
    __slots__ = ("__maximum", "__minimum")

    MINIMUM_TOML_INTEGER: Final[int] = -(2**63)
    MAXIMUM_TOML_INTEGER: Final[int] = (2**63) - 1

    def __init__(
        self, *, minimum: int | None = None, maximum: int | None = None
    ) -> None:
        if minimum is not None:
            if type(minimum) is not int:
                raise TypeError(f"{minimum} must be an integer")
            if (
                minimum < self.MINIMUM_TOML_INTEGER
                or minimum > self.MAXIMUM_TOML_INTEGER
            ):
                raise ValueError(
                    "integer constraint is outside the TOML signed 64-bit range"
                )

        if maximum is not None:
            if type(maximum) is not int:
                raise TypeError(f"{maximum} must be an integer")
            if (
                maximum < self.MINIMUM_TOML_INTEGER
                or maximum > self.MAXIMUM_TOML_INTEGER
            ):
                raise ValueError(
                    "integer constraint is outside the TOML signed 64-bit range"
                )

        if minimum is not None and maximum is not None and minimum > maximum:
            raise ValueError("minimum cannot exceed maximum")

        self.__minimum: int | None = minimum
        self.__maximum: int | None = maximum

    @property
    def minimum(self) -> int | None:
        return self.__minimum

    @property
    def maximum(self) -> int | None:
        return self.__maximum

    def __call__(self, value: int, /) -> None:
        if value < self.MINIMUM_TOML_INTEGER or value > self.MAXIMUM_TOML_INTEGER:
            raise ValueError("integer is outside the TOML signed 64-bit range")

        if self.__minimum is not None and value < self.__minimum:
            raise ValueError("integer is smaller than the minimum")

        if self.__maximum is not None and value > self.__maximum:
            raise ValueError("integer exceeds the maximum")

    def __str__(self) -> str:
        minimum, maximum = (
            tomlkit.dumps(data={"value": value}).rstrip("\n").partition(" = ")[2]
            if value is not None
            else None
            for value in (self.minimum, self.maximum)
        )
        if minimum is not None and maximum is not None:
            return f"Value must be between {minimum} and {maximum}"
        if minimum is not None:
            return f"Value must be at least {minimum}"
        if maximum is not None:
            return f"Value must be at most {maximum}"
        return ""

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}("
            f"minimum={self.__minimum!r}, "
            f"maximum={self.__maximum!r})"
        )
