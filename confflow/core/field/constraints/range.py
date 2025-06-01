from confflow.protocols import Sizeable

from .base_constraint import Constraint


class MinLength(Constraint[Sizeable]):
    def __init__(self, min: int = 1):
        if min < 0:
            raise ValueError("'min' can't be negative.")
        else:
            self._min = min

    def validate(self, value: Sizeable) -> None:
        if len(value) < self._min:
            raise ValueError(f"Length must be at least {self._min}, got {len(value)}.")


class MaxLength(Constraint[Sizeable]):
    def __init__(self, max: int = 1):
        if max < 0:
            raise ValueError("'max' can't be negative.")
        else:
            self._max = max

    def validate(self, value: Sizeable) -> None:
        if len(value) > self._max:
            raise ValueError(f"Length must be at most {self._max}, got {len(value)}.")


class MinValue(Constraint[int | float]):
    def __init__(self, min_value: float):
        self._min = min_value

    def validate(self, value: int | float) -> None:
        if value < self._min:
            raise ValueError(f"Value must be at least {self._min}, got {value}.")
