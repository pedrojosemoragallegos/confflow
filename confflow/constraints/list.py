from confflow.types import Scalar, ScalarList

from .constraint import Constraint


class MinItems(Constraint[ScalarList]):
    def __init__(self, count: int):
        super().__init__(f"List must have at least {count} items")
        self._count: int = count

    def validate(self, value: ScalarList) -> bool:
        return len(value) >= self._count


class MaxItems(Constraint[ScalarList]):
    def __init__(self, count: int):
        super().__init__(f"List must have at most {count} items")
        self._count: int = count

    def validate(self, value: ScalarList) -> bool:
        return len(value) <= self._count


class UniqueItems(Constraint[ScalarList]):
    def __init__(self):
        super().__init__("List items must be unique")

    def validate(self, value: ScalarList) -> bool:
        return len(set(value)) == len(value)


class AllItemsMatch(Constraint[ScalarList]):
    def __init__(self, constraints: list[Constraint[Scalar]]):
        super().__init__(
            f"All list items must match: {', '.join(str(constraint) for constraint in constraints)}"
        )
        self._constraints: list[Constraint[Scalar]] = constraints

    def validate(self, value: ScalarList) -> bool:
        for item in value:
            for constraint in self._constraints:
                if not constraint.validate(item):
                    return False
        return True
