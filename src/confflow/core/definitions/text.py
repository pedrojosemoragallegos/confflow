from __future__ import annotations

from re import compile as compile_pattern, error as regex_error, fullmatch
from typing import Final

from typing_extensions import override

from ..exceptions import InvalidValueError, SchemaError
from ._validation import (
    _validate_integer_bounds,
    _validate_optional_non_negative_integer,
)
from .scalar import Scalar


class Text(Scalar[str]):
    __slots__ = ("_exact_length", "_maximum_length", "_minimum_length", "_pattern")

    @override
    def __init__(
        self,
        name: str,
        description: str = "",
        /,
        *,
        required: bool = False,
        default: str | None = None,
        minimum_length: int | None = None,
        maximum_length: int | None = None,
        exact_length: int | None = None,
        pattern: str | None = None,
    ) -> None:
        _validate_optional_non_negative_integer(minimum_length, "minimum length")
        _validate_optional_non_negative_integer(maximum_length, "maximum length")
        _validate_optional_non_negative_integer(exact_length, "exact length")
        _validate_integer_bounds(minimum_length, maximum_length, "text length")
        if exact_length is not None:
            if minimum_length is not None and exact_length < minimum_length:
                raise SchemaError("exact length cannot be smaller than minimum length")
            if maximum_length is not None and exact_length > maximum_length:
                raise SchemaError("exact length cannot exceed maximum length")
        if pattern is not None:
            if type(pattern) is not str:
                raise SchemaError("text pattern must be a string")
            try:
                compile_pattern(pattern)
            except regex_error as error:
                raise SchemaError(
                    "text pattern must be a valid regular expression"
                ) from error
        self._minimum_length: Final[int | None] = minimum_length
        self._maximum_length: Final[int | None] = maximum_length
        self._exact_length: Final[int | None] = exact_length
        self._pattern: Final[str | None] = pattern
        super().__init__(name, description, required=required, default=default)

    @property
    @override
    def value_type(self) -> type[str]:
        return str

    @override
    def validate(self, value: object, path: tuple[str | int, ...]) -> None:
        if type(value) is not str:
            raise InvalidValueError("expected text", path)
        if (minimum_length := self._minimum_length) is not None and len(
            value
        ) < minimum_length:
            raise InvalidValueError("text is shorter than the minimum length", path)
        if (maximum_length := self._maximum_length) is not None and len(
            value
        ) > maximum_length:
            raise InvalidValueError("text exceeds the maximum length", path)
        if (exact_length := self._exact_length) is not None and len(
            value
        ) != exact_length:
            raise InvalidValueError(
                "text does not have the required exact length", path
            )
        if (pattern := self._pattern) is not None and fullmatch(pattern, value) is None:
            raise InvalidValueError("text does not match the required pattern", path)

    @override
    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}(name={self.name!r}, "
            f"description={self.description!r}, required={self.required!r}, "
            f"default={self.default!r}, "
            f"minimum_length={self._minimum_length!r}, "
            f"maximum_length={self._maximum_length!r}, "
            f"exact_length={self._exact_length!r}, pattern={self._pattern!r})"
        )
