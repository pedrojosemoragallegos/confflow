from __future__ import annotations

from math import isnan
from typing import Final

from typing_extensions import override

from ..exceptions import InvalidValueError
from ._validation import (
    _validate_float_bounds,
    _validate_non_nan_float,
    _validate_optional_float,
)
from .scalar import Scalar


class Decimal(Scalar[float]):
    __slots__ = ("_maximum", "_minimum")

    @override
    def __init__(
        self,
        name: str,
        description: str = "",
        /,
        *,
        required: bool = False,
        default: float | None = None,
        minimum: float | None = None,
        maximum: float | None = None,
    ) -> None:
        _validate_optional_float(minimum, "minimum")
        _validate_optional_float(maximum, "maximum")
        _validate_non_nan_float(minimum, "minimum")
        _validate_non_nan_float(maximum, "maximum")
        _validate_float_bounds(minimum, maximum, "decimal")
        self._minimum: Final[float | None] = minimum
        self._maximum: Final[float | None] = maximum
        super().__init__(name, description, required=required, default=default)

    @property
    @override
    def value_type(self) -> type[float]:
        return float

    @override
    def validate(self, value: object, path: tuple[str | int, ...]) -> None:
        if type(value) is not float:
            raise InvalidValueError("expected a decimal", path)
        if isnan(value):
            raise InvalidValueError("NaN is not allowed", path)
        if (minimum := self._minimum) is not None and value < minimum:
            raise InvalidValueError("decimal is smaller than the minimum", path)
        if (maximum := self._maximum) is not None and value > maximum:
            raise InvalidValueError("decimal exceeds the maximum", path)

    @override
    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}(name={self.name!r}, "
            f"description={self.description!r}, required={self.required!r}, "
            f"default={self.default!r}, "
            f"minimum={self._minimum!r}, maximum={self._maximum!r})"
        )
