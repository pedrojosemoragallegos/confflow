from __future__ import annotations

import re
import typing
from abc import abstractmethod
from re import Pattern

import typing_extensions

from confflow.mixins import FormattedStringMixin

T = typing.TypeVar("T")
TList = typing.TypeVar("TList")

if typing.TYPE_CHECKING:
    from collections.abc import Sequence


## Base Constraint
class ValidationError(Exception, typing.Generic[T]): ...


class Constraint(FormattedStringMixin, typing.Generic[T]):
    @abstractmethod
    def __call__(self, value: T) -> T: ...

    @abstractmethod
    def __repr__(self) -> str: ...


## String Constraints
class MinLength(Constraint[str]):
    def __init__(self, length: int) -> None:
        self._length: int = length

    @typing_extensions.override
    def __call__(self, value: str) -> str:
        def valid(value: str) -> bool:
            return len(value) >= self._length

        if not valid(value):
            raise ValidationError(f"`{value}` not greater than `{self._length}`")  # noqa: EM102, TRY003

        return value

    @typing_extensions.override
    def __repr__(self) -> str:
        return f"MinLength({self._length})"

    @typing_extensions.override
    def to_formatted_string(self, indent: int = 0) -> str:
        return f"Minimum length = {self._length}"


class MaxLength(Constraint[str]):
    def __init__(self, length: int) -> None:
        self._length: int = length

    @typing_extensions.override
    def __call__(self, value: str) -> str:
        def valid(value: str) -> bool:
            return len(value) <= self._length

        if not valid(value):
            raise ValidationError(  # noqa: TRY003
                f"`{value}` exceeds maximum length of `{self._length}`"  # noqa: COM812, EM102
            )

        return value

    @typing_extensions.override
    def __repr__(self) -> str:
        return f"MaxLength({self._length})"

    @typing_extensions.override
    def to_formatted_string(self, indent: int = 0) -> str:
        return f"Maximum length = {self._length}"


class Regex(Constraint[str]):
    def __init__(self, pattern: str) -> None:
        self._pattern: Pattern[str] = re.compile(pattern)

    @typing_extensions.override
    def __call__(self, value: str) -> str:
        if not self._pattern.match(value):
            raise ValidationError(  # noqa: TRY003
                f"`{value}` does not match pattern `{self._pattern!r}`",  # noqa: EM102
            )

        return value

    @typing_extensions.override
    def __repr__(self) -> str:
        return f"Regex({self._pattern!r})"

    @typing_extensions.override
    def to_formatted_string(self, indent: int = 0) -> str:
        return f"Regex: {self._pattern}"


class EnumValues(Constraint[str]):
    def __init__(self, values: Sequence[str]) -> None:
        self._values: list[str] = list(values)

    @typing_extensions.override
    def __call__(self, value: str) -> str:
        if value not in self._values:
            raise ValidationError(f"`{value}` is not one of {self._values!r}")  # noqa: EM102, TRY003

        return value

    @typing_extensions.override
    def __repr__(self) -> str:
        return f"EnumValues({self._values!r})"

    @typing_extensions.override
    def to_formatted_string(self, indent: int = 0) -> str:
        return f"Regex: {self._values!r}"


## Numeric Constraints
TNumber = typing.TypeVar("TNumber", int, float)


class GreaterThan(Constraint[TNumber]):
    def __init__(self, threshold: TNumber) -> None:
        self._threshold: TNumber = threshold

    @typing_extensions.override
    def __call__(self, value: TNumber) -> TNumber:
        if not value > self._threshold:
            raise ValidationError(f"`{value}` is not greater than `{self._threshold}`")  # noqa: EM102, TRY003

        return value

    @typing_extensions.override
    def __repr__(self) -> str:
        return f"GreaterThan({self._threshold!r})"

    @typing_extensions.override
    def to_formatted_string(self, indent: int = 0) -> str:
        return f"Greater than: {self._threshold!r}"


class GreaterThanOrEqual(Constraint[TNumber]):
    def __init__(self, threshold: TNumber) -> None:
        self._threshold: TNumber = threshold

    @typing_extensions.override
    def __call__(self, value: TNumber) -> TNumber:
        if not value >= self._threshold:
            raise ValidationError(f"`{value}` is not >= `{self._threshold}`")  # noqa: EM102, TRY003

        return value

    @typing_extensions.override
    def __repr__(self) -> str:
        return f"GreaterThanOrEqual({self._threshold!r})"

    @typing_extensions.override
    def to_formatted_string(self, indent: int = 0) -> str:
        return f"Greater than or equal: {self._threshold!r}"


class LessThan(Constraint[TNumber]):
    def __init__(self, threshold: TNumber) -> None:
        self._threshold: TNumber = threshold

    @typing_extensions.override
    def __call__(self, value: TNumber) -> TNumber:
        if not value < self._threshold:
            raise ValidationError(f"`{value}` is not less than `{self._threshold}`")  # noqa: EM102, TRY003

        return value

    @typing_extensions.override
    def __repr__(self) -> str:
        return f"LessThan({self._threshold!r})"

    @typing_extensions.override
    def to_formatted_string(self, indent: int = 0) -> str:
        return f"Less than: {self._threshold!r}"


class LessThanOrEqual(Constraint[TNumber]):
    def __init__(self, threshold: TNumber) -> None:
        self._threshold: TNumber = threshold

    @typing_extensions.override
    def __call__(self, value: TNumber) -> TNumber:
        if not value <= self._threshold:
            raise ValidationError(f"`{value}` is not <= `{self._threshold}`")  # noqa: EM102, TRY003

        return value

    @typing_extensions.override
    def __repr__(self) -> str:
        return f"LessThanOrEqual({self._threshold!r})"

    @typing_extensions.override
    def to_formatted_string(self, indent: int = 0) -> str:
        return f"Less than or equal: {self._threshold!r}"


## List Constraints
class ListMinLength(Constraint[list[TList]]):
    def __init__(self, length: int) -> None:
        self._length: int = length

    @typing_extensions.override
    def __call__(self, value: list[TList]) -> list[TList]:
        def valid(value: list[TList]) -> bool:
            return len(value) >= self._length

        if not valid(value):
            raise ValidationError(  # noqa: TRY003
                f"Length {len(value)} is not >= minimum length {self._length}",  # noqa: EM102
            )

        return value

    @typing_extensions.override
    def __repr__(self) -> str:
        return f"MinLength({self._length})"

    @typing_extensions.override
    def to_formatted_string(self, indent: int = 0) -> str:
        return f"Minimum length = {self._length}"


class ListMaxLength(Constraint[list[TList]]):
    def __init__(self, length: int) -> None:
        self._length: int = length

    @typing_extensions.override
    def __call__(self, value: list[TList]) -> list[TList]:
        def valid(value: list[TList]) -> bool:
            return len(value) <= self._length

        if not valid(value):
            raise ValidationError(  # noqa: TRY003
                f"Length {len(value)} exceeds maximum length of {self._length}"  # noqa: COM812, EM102
            )

        return value

    @typing_extensions.override
    def __repr__(self) -> str:
        return f"MaxLength({self._length})"

    @typing_extensions.override
    def to_formatted_string(self, indent: int = 0) -> str:
        return f"Maximum length = {self._length}"
