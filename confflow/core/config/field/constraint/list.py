from typing import Any

from .constraint import Constraint


class MinItems(Constraint[list[Any]]):
    def __init__(self, count: int):
        super().__init__(f"List must have at least {count} items")
        self._count = count

    def validate(self, value: list[Any]) -> bool:
        return len(value) >= self._count

    def __repr__(self) -> str:  # TODO find a better way to not repeat
        return f"{self.__class__.__name__}({self._count})"


class MaxItems(Constraint[list[Any]]):
    def __init__(self, count: int):
        super().__init__(f"List must have at most {count} items")
        self._count = count

    def validate(self, value: list[Any]) -> bool:
        return len(value) <= self._count

    def __repr__(self) -> str:  # TODO find a better way to not repeat
        return f"{self.__class__.__name__}({self._count})"


class UniqueItems(Constraint[list[Any]]):
    def __init__(self):
        super().__init__("List items must be unique")

    def validate(self, value: list[Any]) -> bool:
        return len(set(value)) == len(value)

    def __repr__(self) -> str:  # TODO find a better way to not repeat
        return f"{self.__class__.__name__}()"
