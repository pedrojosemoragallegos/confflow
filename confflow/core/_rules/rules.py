from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, Set, TypeVar

T = TypeVar("T")


class BaseRule(ABC, Generic[T]):
    def __init__(self):
        self._items: Set[T] = set()

    def add_item(self, item: T) -> BaseRule[T]:
        self._items.add(item)
        return self

    def add_items(self, *items: T) -> BaseRule[T]:
        for item in items:
            self._items.add(item)
        return self

    @abstractmethod
    def validate(self, selection: Set[T]) -> bool: ...

    @property
    def items(self) -> Set[T]:
        return self._items


class MutuallyExclusive(BaseRule[T]):
    def validate(self, selection: Set[T]) -> bool:
        return len(self._items & selection) <= 1


class AllOrNone(BaseRule[T]):
    def validate(self, selection: Set[T]) -> bool:
        selected = self._items & selection
        return len(selected) == 0 or selected == self._items


class OneOfGroup(BaseRule[T]):
    def validate(self, selection: Set[T]) -> bool:
        return len(self._items & selection) == 1


class ExactlyN(BaseRule[T]):
    def __init__(self, n: int):
        super().__init__()
        self._n = n

    def add_item(self, item: T) -> ExactlyN[T]:
        if len(self._items) >= self._n:
            raise ValueError(
                f"Cannot add more than {self._n} items to rule '{self.__class__.__name__}'"
            )
        super().add_item(item)
        return self

    def add_items(self, *items: T) -> ExactlyN[T]:
        if len(self._items) + len(items) > self._n:
            raise ValueError(
                f"Cannot add more than {self._n} items to rule '{self.__class__.__name__}'"
            )
        return super().add_items(*items)

    def validate(self, selection: Set[T]) -> bool:
        return len(self._items & selection) == self._n


class RequiresOneOf(BaseRule[T]):
    def __init__(self, trigger: T):
        super().__init__()
        self._trigger = trigger

    def add_item(self, item: T) -> RequiresOneOf[T]:
        if item == self._trigger:
            raise ValueError("Cannot add the trigger to its own required set.")
        super().add_item(item)
        return self

    def add_items(self, *items: T) -> RequiresOneOf[T]:
        if self._trigger in items:
            raise ValueError("Cannot add the trigger to its own required set.")
        return super().add_items(*items)

    def validate(self, selection: Set[T]) -> bool:
        if self._trigger in selection:
            return bool(self._items & selection)
        return True


class RequiresAll(BaseRule[T]):
    def __init__(self, trigger: T):
        super().__init__()
        self._trigger = trigger

    def add_item(self, item: T) -> RequiresAll[T]:
        if item == self._trigger:
            raise ValueError("Cannot add the trigger to its own required set.")
        super().add_item(item)
        return self

    def add_items(self, *items: T) -> RequiresAll[T]:
        if self._trigger in items:
            raise ValueError("Cannot add the trigger to its own required set.")
        return super().add_items(*items)

    def validate(self, selection: Set[T]) -> bool:
        if self._trigger in selection:
            return self._items.issubset(selection)
        return True


class Excludes(BaseRule[T]):
    def __init__(self, trigger: T):
        super().__init__()
        self._trigger = trigger

    def add_item(self, item: T) -> Excludes[T]:
        if item == self._trigger:
            raise ValueError("Cannot add the trigger to its own exclusion set.")
        super().add_item(item)
        return self

    def add_items(self, *items: T) -> Excludes[T]:
        if self._trigger in items:
            raise ValueError("Cannot add the trigger to its own exclusion set.")
        return super().add_items(*items)

    def validate(self, selection: Set[T]) -> bool:
        if self._trigger in selection:
            return len(self._items & selection) == 0
        return True


class AtLeastN(BaseRule[T]):
    def __init__(self, n: int):
        super().__init__()
        self._n = n

    def validate(self, selection: Set[T]) -> bool:
        return len(self._items & selection) >= self._n


class NotAll(BaseRule[T]):
    def validate(self, selection: Set[T]) -> bool:
        return (self._items & selection) != self._items
