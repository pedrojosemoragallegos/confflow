from __future__ import annotations

import re
import typing
from re import Pattern

from .constraint import Constraint

if typing.TYPE_CHECKING:
    from collections.abc import Sequence


class MinLength(Constraint[str]):
    def __init__(self, length: int) -> None:
        super().__init__(f"Value must be at least {length} characters long")
        self._length: int = length

    def validate(self, value: str) -> bool:
        return len(value) >= self._length


class MaxLength(Constraint[str]):
    def __init__(self, length: int) -> None:
        super().__init__(f"Value must be at most {length} characters long")
        self._length: int = length

    def validate(self, value: str) -> bool:
        return len(value) <= self._length


class Regex(Constraint[str]):
    def __init__(self, pattern: str) -> None:
        super().__init__(f"Value must match pattern {pattern}")
        self._pattern: Pattern[str] = re.compile(pattern)

    def validate(self, value: str) -> bool:
        return bool(self._pattern.match(value))


class EnumValues(Constraint[str]):
    def __init__(self, values: Sequence[str]) -> None:
        super().__init__(f"Value must be one of {list(values)}")
        self._values: set[str] = set(values)

    def validate(self, value: str) -> bool:
        return value in self._values
