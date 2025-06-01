import re

from .base_constraint import Constraint


class Pattern(Constraint[str]):
    def __init__(self, pattern: str):
        self._regex = re.compile(pattern)

    def validate(self, value: str) -> None:
        if not self._regex.fullmatch(value):
            raise ValueError(
                f"Value '{value}' does not match pattern '{self._regex.pattern}'."
            )
