from __future__ import annotations

from typing import Final

from confflow.core.constraints.base import Constraint


class Range(Constraint[int]):
    __slots__ = ("__maximum", "__minimum")

    NAME: Final[str] = "range"

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

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}("
            f"minimum={self.__minimum!r}, "
            f"maximum={self.__maximum!r})"
        )
