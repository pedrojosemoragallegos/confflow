from typing import TypeVar

from confflow.types import Value

from .constraint import Constraint

T = TypeVar("T", bound=Value)


class MinItems(Constraint[list[T]]):  # type: ignore
    def __init__(self, count: int):
        super().__init__(f"List must have at least {count} items")
        self._count = count

    def validate(self, value: list[T]) -> bool:
        return len(value) >= self._count


class MaxItems(Constraint[list[T]]):  # type: ignore
    def __init__(self, count: int):
        super().__init__(f"List must have at most {count} items")
        self._count = count

    def validate(self, value: list[T]) -> bool:
        return len(value) <= self._count


class UniqueItems(Constraint[list[T]]):  # type: ignore
    def __init__(self):
        super().__init__("List items must be unique")

    def validate(self, value: list[T]) -> bool:
        return len(set(value)) == len(value)


class AllItemsMatch(Constraint[list[T]]):  # type: ignore
    def __init__(self, constraints: list[Constraint[T]]) -> None:
        super().__init__(
            f"All list items must match: {', '.join(str(constraint) for constraint in constraints)}"
        )
        self._constraints: list[Constraint[T]] = constraints

    def validate(self, value: list[T]) -> bool:
        for item in value:
            for constraint in self._constraints:
                if not constraint.validate(item):
                    return False
        return True
