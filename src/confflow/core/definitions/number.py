from __future__ import annotations

from typing import ClassVar, Final

from typing_extensions import override

from ..exceptions import InvalidValueError
from ._validation import (
    _validate_integer_bounds,
    _validate_optional_integer,
    _validate_toml_integer,
)
from .scalar import Scalar


class Number(Scalar[int]):
    __slots__ = ("_maximum", "_minimum")

    MINIMUM_TOML_INTEGER: ClassVar[int] = -(2**63)
    MAXIMUM_TOML_INTEGER: ClassVar[int] = (2**63) - 1

    @override
    def __init__(
        self,
        name: str,
        description: str = "",
        /,
        *,
        required: bool = False,
        default: int | None = None,
        minimum: int | None = None,
        maximum: int | None = None,
    ) -> None:
        _validate_optional_integer(minimum, "minimum")
        _validate_optional_integer(maximum, "maximum")
        _validate_toml_integer(
            minimum, self.MINIMUM_TOML_INTEGER, self.MAXIMUM_TOML_INTEGER
        )
        _validate_toml_integer(
            maximum, self.MINIMUM_TOML_INTEGER, self.MAXIMUM_TOML_INTEGER
        )
        _validate_integer_bounds(minimum, maximum, "number")
        self._minimum: Final[int | None] = minimum
        self._maximum: Final[int | None] = maximum
        super().__init__(name, description, required=required, default=default)

    @property
    @override
    def value_type(self) -> type[int]:
        return int

    @override
    def validate(self, value: object, path: tuple[str | int, ...]) -> None:
        if type(value) is not int:
            raise InvalidValueError("expected a number", path)
        if value < self.MINIMUM_TOML_INTEGER or value > self.MAXIMUM_TOML_INTEGER:
            raise InvalidValueError(
                "number is outside the TOML signed 64-bit range", path
            )
        if (minimum := self._minimum) is not None and value < minimum:
            raise InvalidValueError("number is smaller than the minimum", path)
        if (maximum := self._maximum) is not None and value > maximum:
            raise InvalidValueError("number exceeds the maximum", path)

    @override
    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}(name={self.name!r}, "
            f"description={self.description!r}, required={self.required!r}, "
            f"default={self.default!r}, "
            f"minimum={self._minimum!r}, maximum={self._maximum!r})"
        )
