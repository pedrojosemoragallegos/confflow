from __future__ import annotations

import math

from typing_extensions import override

from confflow.core.shared import ConfigurationError

from .base import Field


class Float(Field[float]):
    def __init__(
        self,
        name: str,
        description: str,
        /,
        *,
        required: bool = False,
        default: float | None = None,
        minimum: float | None = None,
        maximum: float | None = None,
    ) -> None:
        if minimum is not None and math.isnan(minimum):
            msg = "minimum cannot be NaN"
            raise ValueError(msg)

        if maximum is not None and math.isnan(maximum):
            msg = "maximum cannot be NaN"
            raise ValueError(msg)

        if minimum is not None and maximum is not None and minimum > maximum:
            msg = "minimum cannot exceed maximum"
            raise ValueError(msg)

        self._minimum: float | None = minimum
        self._maximum: float | None = maximum

        super().__init__(name, description, required=required, default=default)

    @property
    def minimum(self) -> float | None:
        return self._minimum

    @property
    def maximum(self) -> float | None:
        return self._maximum

    @override
    def _typecheck(self, value: object, /) -> bool:
        return type(value) is float

    @override
    def validate(self, value: object, path: str, /) -> float:
        value: float = super().validate(value, path)

        if self.minimum is not None and value < self.minimum:
            raise ConfigurationError(path, f"must be >= {self.minimum}")

        if self.maximum is not None and value > self.maximum:
            raise ConfigurationError(path, f"must be <= {self.maximum}")

        return value
