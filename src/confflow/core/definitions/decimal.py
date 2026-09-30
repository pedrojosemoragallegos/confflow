from __future__ import annotations

from math import isnan
from typing import ClassVar, Final

from typing_extensions import override

from ._validators import (
    validate_float,
    validate_float_bounds,
    validate_non_nan_float,
)
from .base import Definition
from .exceptions import DefinitionError


class Decimal(Definition[float]):
    __slots__ = ("__maximum", "__minimum")

    VALUE_TYPE: ClassVar[type[float]] = float

    @override
    def __init__(
        self,
        *,
        minimum: float | None = None,
        maximum: float | None = None,
    ) -> None:
        if minimum is not None:
            validate_float(value=minimum, label="minimum")
            validate_non_nan_float(value=minimum, label="minimum")

        if maximum is not None:
            validate_float(value=maximum, label="maximum")
            validate_non_nan_float(value=maximum, label="maximum")

        if minimum is not None and maximum is not None:
            validate_float_bounds(minimum=minimum, maximum=maximum, label="decimal")

        self.__minimum: Final[float | None] = minimum
        self.__maximum: Final[float | None] = maximum

    @override
    def validate(self, value: object) -> None:
        if type(value) is not float:
            raise DefinitionError("expected a decimal")

        if isnan(value):
            raise DefinitionError("NaN is not allowed")

        if (minimum := self.__minimum) is not None and value < minimum:
            raise DefinitionError("decimal is smaller than the minimum")

        if (maximum := self.__maximum) is not None and value > maximum:
            raise DefinitionError("decimal exceeds the maximum")

    @override
    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}("
            f"minimum={self.__minimum!r}, maximum={self.__maximum!r})"
        )
