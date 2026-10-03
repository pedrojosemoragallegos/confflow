from __future__ import annotations

from datetime import date
from typing import Final

import tomlkit

from .base import Constraint


class LocalDate(Constraint[date]):
    __slots__ = ()


class Range(LocalDate):
    __slots__ = ("__maximum", "__minimum")

    def __init__(
        self, *, minimum: date | None = None, maximum: date | None = None
    ) -> None:
        for value in (minimum, maximum):
            if value is not None and type(value) is not date:
                raise ValueError("value must be a date")

        if minimum is not None and maximum is not None and minimum > maximum:
            raise ValueError("minimum cannot exceed maximum")

        self.__minimum: Final[date | None] = minimum
        self.__maximum: Final[date | None] = maximum

    @property
    def minimum(self) -> date | None:
        return self.__minimum

    @property
    def maximum(self) -> date | None:
        return self.__maximum

    def __call__(self, value: date, /) -> None:
        if self.__minimum is not None and value < self.__minimum:
            raise ValueError("date is smaller than the minimum")

        if self.__maximum is not None and value > self.__maximum:
            raise ValueError("date exceeds the maximum")

    def __str__(self) -> str:
        minimum, maximum = (
            tomlkit.dumps({"value": value}).rstrip("\n").partition(" = ")[2]
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
