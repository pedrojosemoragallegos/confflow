from __future__ import annotations

from typing import ClassVar

from typing_extensions import override

from confflow.core.shared import TOML_INT_MAX, TOML_INT_MIN, ConfigurationError

from .base import Field


class Integer(Field[int]):
    option_names: ClassVar[tuple[str, ...]] = ("minimum", "maximum")

    __slots__ = ("_maximum", "_minimum")

    def __init__(
        self,
        name: str,
        description: str,
        /,
        *,
        required: bool = False,
        default: int | None = None,
        minimum: int | None = None,
        maximum: int | None = None,
    ) -> None:
        if minimum is not None and maximum is not None and minimum > maximum:
            msg = "minimum cannot exceed maximum"
            raise ValueError(msg)

        self._minimum: int | None = minimum
        self._maximum: int | None = maximum

        super().__init__(name, description, required=required, default=default)

    @property
    def minimum(self) -> int | None:
        return self._minimum

    @property
    def maximum(self) -> int | None:
        return self._maximum

    @override
    def _typecheck(self, value: object, /) -> bool:
        return type(value) is int and TOML_INT_MIN <= value <= TOML_INT_MAX

    @override
    def validate(self, value: object, path: str, /) -> int:
        value: int = super().validate(value, path)

        if self.minimum is not None and value < self.minimum:
            raise ConfigurationError(path, f"must be >= {self.minimum}")

        if self.maximum is not None and value > self.maximum:
            raise ConfigurationError(path, f"must be <= {self.maximum}")

        return value
