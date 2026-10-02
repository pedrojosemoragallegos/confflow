from __future__ import annotations

from datetime import datetime
from typing import Final

from .base import Constraint


class LocalDateTime(Constraint[datetime]):
    __slots__ = ()


class Range(LocalDateTime):
    __slots__ = ("__maximum", "__minimum")

    NAME: Final[str] = "range"

    def __init__(
        self,
        *,
        minimum: datetime | None = None,
        maximum: datetime | None = None,
    ) -> None:
        for value in (minimum, maximum):
            if value is not None and (
                type(value) is not datetime
                or (value.tzinfo is not None and value.utcoffset() is not None)
            ):
                raise ValueError("value must be a timezone-naive datetime")

        if minimum is not None and maximum is not None and minimum > maximum:
            raise ValueError("minimum cannot exceed maximum")

        self.__minimum: datetime | None = minimum
        self.__maximum: datetime | None = maximum

    @property
    def minimum(self) -> datetime | None:
        return self.__minimum

    @property
    def maximum(self) -> datetime | None:
        return self.__maximum

    def __call__(self, value: datetime, /) -> None:
        if self.__minimum is not None and value < self.__minimum:
            raise ValueError("date-time is smaller than the minimum")

        if self.__maximum is not None and value > self.__maximum:
            raise ValueError("date-time exceeds the maximum")

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}("
            f"minimum={self.__minimum!r}, "
            f"maximum={self.__maximum!r})"
        )
