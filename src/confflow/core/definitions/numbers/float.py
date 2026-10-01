from __future__ import annotations

from math import isnan
from typing import ClassVar, Final

from typing_extensions import override

from confflow.core.definitions.base import Definition
from confflow.core.definitions.exceptions import ValidationError

from ._validators import (
    validate_float,
    validate_float_bounds,
    validate_non_nan_float,
)


class Float(Definition[float]):
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
            validate_float("minimum", value=minimum)
            validate_non_nan_float("minimum", value=minimum)

        if maximum is not None:
            validate_float("maximum", value=maximum)
            validate_non_nan_float("maximum", value=maximum)

        if minimum is not None and maximum is not None:
            validate_float_bounds("float", minimum=minimum, maximum=maximum)

        self.__minimum: Final[float | None] = minimum
        self.__maximum: Final[float | None] = maximum

    @override
    def validate(self, value: object) -> None:
        if type(value) is not float:
            raise ValidationError("expected a float")

        if isnan(value):
            raise ValidationError("NaN is not allowed")

        if (minimum := self.__minimum) is not None and value < minimum:
            raise ValidationError("float is smaller than the minimum")

        if (maximum := self.__maximum) is not None and value > maximum:
            raise ValidationError("float exceeds the maximum")

    @override
    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}("
            f"minimum={self.__minimum!r}, maximum={self.__maximum!r})"
        )
