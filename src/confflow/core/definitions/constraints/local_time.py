from __future__ import annotations

from datetime import time
from typing import Final

from .base import Constraint


class LocalTime(Constraint[time]):
    __slots__ = ()


class Range(LocalTime):
    __slots__ = ("__maximum", "__minimum")

    NAME: Final[str] = "range"

    def __init__(
        self,
        *,
        minimum: time | None = None,
        maximum: time | None = None,
    ) -> None:
        for value in (minimum, maximum):
            if value is not None and (
                type(value) is not time
                or (value.tzinfo is not None and value.utcoffset() is not None)
            ):
                raise ValueError("value must be a timezone-naive time")

        if minimum is not None and maximum is not None and minimum > maximum:
            raise ValueError("minimum cannot exceed maximum")

        self.__minimum: time | None = minimum
        self.__maximum: time | None = maximum

    @property
    def minimum(self) -> time | None:
        return self.__minimum

    @property
    def maximum(self) -> time | None:
        return self.__maximum

    def __call__(self, value: time, /) -> None:
        if self.__minimum is not None and value < self.__minimum:
            raise ValueError("time is smaller than the minimum")

        if self.__maximum is not None and value > self.__maximum:
            raise ValueError("time exceeds the maximum")

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}("
            f"minimum={self.__minimum!r}, "
            f"maximum={self.__maximum!r})"
        )
