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
            raise ValueError("Not satisfied.")  # TODO correct message


class MaxLength(Constraint[Sizeable]):
    def __init__(self, max: int = 1):
        if max < 0:
            raise ValueError("'max' can't be negative.")
        else:
            self._max = max

    def validate(self, value: Sizeable) -> None:
        if len(value) > self._max:
            raise ValueError("Not satisfied.")  # TODO correct message
