from .constraint import Constraint


class MinItems(Constraint[list]):
    def __init__(self, count: int) -> None:
        super().__init__(f"List must have at least {count} items")
        self._count = count

    def validate(self, value: list) -> bool:
        return len(value) >= self._count


class MaxItems(Constraint[list]):
    def __init__(self, count: int) -> None:
        super().__init__(f"List must have at most {count} items")
        self._count = count

    def validate(self, value: list) -> bool:
        return len(value) <= self._count


class UniqueItems(Constraint[list]):
    def __init__(self) -> None:
        super().__init__("List items must be unique")

    def validate(self, value: list) -> bool:
        return len(set(value)) == len(value)
