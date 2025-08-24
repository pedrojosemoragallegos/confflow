import re
from typing import Sequence

from .constraint import Constraint


class MinLength(Constraint[str]):
    def __init__(self, length: int):
        super().__init__(f"Value must be at least {length} characters long")
        self._length = length

    def validate(self, value: str) -> bool:
        return len(value) >= self._length


class MaxLength(Constraint[str]):
    def __init__(self, length: int):
        super().__init__(f"Value must be at most {length} characters long")
        self._length = length

    def validate(self, value: str) -> bool:
        return len(value) <= self._length


class Regex(Constraint[str]):
    def __init__(self, pattern: str):
        super().__init__(f"Value must match pattern {pattern}")
        self._pattern = re.compile(pattern)

    def validate(self, value: str) -> bool:
        return bool(self._pattern.match(value))


class EnumValues(Constraint[str]):
    def __init__(self, values: Sequence[str]):
        super().__init__(f"Value must be one of {list(values)}")
        self._values = set(values)

    def validate(self, value: str) -> bool:
        return value in self._values
