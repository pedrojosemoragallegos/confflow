from __future__ import annotations

from datetime import date
from typing import Final

from .base import Constraint


class Range(Constraint[date]):
    __slots__ = ("__maximum", "__minimum")

    NAME: Final[str] = "range"

    def __init__(
        self, *, minimum: date | None = None, maximum: date | None = None
    ) -> None:
        for value in (minimum, maximum):
            if value is not None and type(value) is not date:
                raise ValueError("value must be a date")

        if minimum is not None and maximum is not None and minimum > maximum:
            raise ValueError("minimum cannot exceed maximum")

        self.__minimum: date | None = minimum
        self.__maximum: date | None = maximum

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

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}("
            f"minimum={self.__minimum!r}, "
            f"maximum={self.__maximum!r})"
        )
