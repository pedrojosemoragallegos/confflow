from __future__ import annotations

from typing import ClassVar, Final

from typing_extensions import override

from confflow.core.definitions.base import Definition
from confflow.core.definitions.exceptions import ValidationError

from ._validators import (
    validate_integer,
    validate_integer_bounds,
    validate_toml_integer,
)


class Integer(Definition[int]):
    __slots__ = ("__maximum", "__minimum")

    VALUE_TYPE: ClassVar[type[int]] = int

    MINIMUM_TOML_INTEGER: ClassVar[int] = -(2**63)
    MAXIMUM_TOML_INTEGER: ClassVar[int] = (2**63) - 1

    @override
    def __init__(
        self,
        *,
        minimum: int | None = None,
        maximum: int | None = None,
    ) -> None:
        if minimum is not None:
            validate_integer("minimum", value=minimum)
            validate_toml_integer(
                value=minimum,
                minimum=self.MINIMUM_TOML_INTEGER,
                maximum=self.MAXIMUM_TOML_INTEGER,
            )
        if maximum is not None:
            validate_integer("maximum", value=maximum)
            validate_toml_integer(
                value=maximum,
                minimum=self.MINIMUM_TOML_INTEGER,
                maximum=self.MAXIMUM_TOML_INTEGER,
            )
        if minimum is not None and maximum is not None:
            validate_integer_bounds("integer", minimum=minimum, maximum=maximum)

        self.__minimum: Final[int | None] = minimum
        self.__maximum: Final[int | None] = maximum

    @override
    def validate(self, value: object) -> None:
        if type(value) is not int:
            raise ValidationError("expected an integer")

        if value < self.MINIMUM_TOML_INTEGER or value > self.MAXIMUM_TOML_INTEGER:
            raise ValidationError("number is outside the TOML signed 64-bit range")

        if (minimum := self.__minimum) is not None and value < minimum:
            raise ValidationError("integer is smaller than the minimum")

        if (maximum := self.__maximum) is not None and value > maximum:
            raise ValidationError("integer exceeds the maximum")

    @override
    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}("
            f"minimum={self.__minimum!r}, maximum={self.__maximum!r})"
        )
