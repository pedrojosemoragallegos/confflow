from typing import TypeVar

from confflow.types import Scalar, ScalarList

from .constraint import Constraint

T = TypeVar("T", bound=ScalarList)


class MinItems(Constraint[T]):
    def __init__(self, count: int):
        super().__init__(f"List must have at least {count} items")
        self._count: int = count

    def validate(self, value: T) -> bool:
        return len(value) >= self._count


class MaxItems(Constraint[T]):
    def __init__(self, count: int):
        super().__init__(f"List must have at most {count} items")
        self._count: int = count

    def validate(self, value: T) -> bool:
        return len(value) <= self._count


class UniqueItems(Constraint[T]):
    def __init__(self):
        super().__init__("List items must be unique")

    def validate(self, value: T) -> bool:
        return len(set(value)) == len(value)


class AllItemsMatch(Constraint[T]):
    def __init__(self, *constraints: Constraint[Scalar]):
        super().__init__(
            f"All list items must match: {', '.join(str(constraint) for constraint in constraints)}"
        )
        self._constraints: tuple[Constraint[Scalar], ...] = constraints

    def validate(self, value: T) -> bool:
        for item in value:
            for constraint in self._constraints:
                if not constraint.validate(item):
                    return False
        return True
