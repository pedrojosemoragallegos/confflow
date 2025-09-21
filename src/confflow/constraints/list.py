from __future__ import annotations

import typing
from datetime import datetime

from .constraint import Constraint

T = typing.TypeVar(
    "T",
    list[str],
    list[int],
    list[float],
    list[bool],
    list[datetime],
    list[bytes],
)
E = typing.TypeVar("E", str, int, float, bool, datetime, bytes)


class MinItems(Constraint[T]):
    def __init__(self, count: int) -> None:
        super().__init__(f"List must have at least {count} items")
        self._count: int = count

    def validate(self, value: T) -> bool:
        return len(value) >= self._count


class MaxItems(Constraint[T]):
    def __init__(self, count: int) -> None:
        super().__init__(f"List must have at most {count} items")
        self._count: int = count

    def validate(self, value: T) -> bool:
        return len(value) <= self._count


class UniqueItems(Constraint[T]):
    def __init__(self) -> None:
        super().__init__("List items must be unique")

    def validate(self, value: T) -> bool:
        return len(set(value)) == len(value)


class AllItemsMatch(Constraint[list[E]], typing.Generic[E]):
    def __init__(
        self,
        *constraints: Constraint[E],
    ) -> None:
        super().__init__(
            f"All list items must match: {', '.join(str(constraint) for constraint in constraints)}",  # noqa: E501
        )
        self._constraints: tuple[
            Constraint[E],
            ...,
        ] = constraints

    def validate(self, value: list[E]) -> bool:
        for item in value:
            for constraint in self._constraints:
                if not constraint.validate(item):
                    return False
        return True
