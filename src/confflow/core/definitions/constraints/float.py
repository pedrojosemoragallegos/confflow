from __future__ import annotations

from math import isnan
from typing import Final

from typing_extensions import override

from .base import Constraint


class Float(Constraint[float]):
    __slots__ = ()


class Range(Float):
    __slots__ = ("__maximum", "__minimum")

    NAME: Final[str] = "range"

    def __init__(
        self, *, minimum: float | None = None, maximum: float | None = None
    ) -> None:
        for value in (minimum, maximum):
            if value is not None:
                if type(value) is not float:
                    raise TypeError(f"{value} must be a float")
                if isnan(value):
                    raise ValueError(f"{value} cannot be NaN")

        if minimum is not None and maximum is not None and minimum > maximum:
            raise ValueError(" minimum cannot exceed maximum")

        self.__minimum: Final[float | None] = minimum
        self.__maximum: Final[float | None] = maximum

    @property
    def minimum(self) -> float | None:
        return self.__minimum

    @property
    def maximum(self) -> float | None:
        return self.__maximum

    @override
    def __call__(self, value: float, /) -> None:
        if self.__minimum is not None and value < self.__minimum:
            raise ValueError("float is smaller than the minimum")

        if self.__maximum is not None and value > self.__maximum:
            raise ValueError("float exceeds the maximum")

    @override
    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}("
            f"minimum={self.__minimum!r}, "
            f"maximum={self.__maximum!r})"
        )


class NotNaN(Float):
    __slots__ = ()

    NAME: Final[str] = "not_nan"

    @override
    def __call__(self, value: float, /) -> None:
        if isnan(value):
            raise ValueError("NaN is not allowed")

    @override
    def __repr__(self) -> str:
        return f"{type(self).__name__}()"
