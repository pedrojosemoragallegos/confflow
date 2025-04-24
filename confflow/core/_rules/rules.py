from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, Set, TypeVar

T = TypeVar("T")


class ValidationError(Exception):
    """Raised when a rule validation fails."""

    pass


class BaseRule(ABC, Generic[T]):
    def __init__(self):
        self._items: Set[T] = set()

    @property
    def items(self) -> Set[T]:
        return self._items

    def add_item(self, item: T) -> BaseRule[T]:
        self._items.add(item)
        return self

    def add_items(self, *items: T) -> BaseRule[T]:
        for item in items:
            self._items.add(item)
        return self

    @abstractmethod
    def validate(self, *selection: T) -> bool:
        """Raises ValidationError if the rule is not satisfied."""
        ...


class MutuallyExclusive(BaseRule[T]):
    def validate(self, *selection: T) -> bool:
        if len(self._items & set(selection)) > 1:
            raise ValidationError(f"Only one of {self._items} can be selected.")
        return True


class AllOrNone(BaseRule[T]):
    def validate(self, *selection: T) -> bool:
        selected = self._items & set(selection)
        if 0 < len(selected) < len(self._items):
            raise ValidationError(f"Must select all or none of {self._items}.")
        return True


class OneOfGroup(BaseRule[T]):
    def validate(self, *selection: T) -> bool:
        if len(self._items & set(selection)) != 1:
            raise ValidationError(f"Exactly one of {self._items} must be selected.")
        return True


class ExactlyN(BaseRule[T]):
    def __init__(self, n: int):
        super().__init__()
        self._n = n

    def add_item(self, item: T) -> ExactlyN[T]:
        if len(self._items) >= self._n:
            raise ValueError(f"Cannot add more than {self._n} items.")
        return super().add_item(item)

    def add_items(self, *items: T) -> ExactlyN[T]:
        if len(self._items) + len(items) > self._n:
            raise ValueError(f"Cannot add more than {self._n} items.")
        return super().add_items(*items)

    def validate(self, *selection: T) -> bool:
        if len(self._items & set(selection)) != self._n:
            raise ValidationError(
                f"Exactly {self._n} of {self._items} must be selected."
            )
        return True


class RequiresOneOf(BaseRule[T]):
    def __init__(self, trigger: T):
        super().__init__()
        self._trigger = trigger

    def add_item(self, item: T) -> RequiresOneOf[T]:
        if item == self._trigger:
            raise ValueError("Trigger cannot be in the required set.")
        return super().add_item(item)

    def add_items(self, *items: T) -> RequiresOneOf[T]:
        if self._trigger in items:
            raise ValueError("Trigger cannot be in the required set.")
        return super().add_items(*items)

    def validate(self, *selection: T) -> bool:
        if self._trigger in selection and not (self._items & set(selection)):
            raise ValidationError(
                f"If '{self._trigger}' is selected, at least one of {self._items} must also be selected."
            )
        return True


class RequiresAll(BaseRule[T]):
    def __init__(self, trigger: T):
        super().__init__()
        self._trigger = trigger

    def add_item(self, item: T) -> RequiresAll[T]:
        if item == self._trigger:
            raise ValueError("Trigger cannot be in the required set.")
        return super().add_item(item)

    def add_items(self, *items: T) -> RequiresAll[T]:
        if self._trigger in items:
            raise ValueError("Trigger cannot be in the required set.")
        return super().add_items(*items)

    def validate(self, *selection: T) -> bool:
        if self._trigger in selection and not self._items.issubset(selection):
            raise ValidationError(
                f"If '{self._trigger}' is selected, all of {self._items} must also be selected."
            )
        return True


class Excludes(BaseRule[T]):
    def __init__(self, trigger: T):
        super().__init__()
        self._trigger = trigger

    def add_item(self, item: T) -> Excludes[T]:
        if item == self._trigger:
            raise ValueError("Trigger cannot be in its own exclusion set.")
        return super().add_item(item)

    def add_items(self, *items: T) -> Excludes[T]:
        if self._trigger in items:
            raise ValueError("Trigger cannot be in its own exclusion set.")
        return super().add_items(*items)

    def validate(self, *selection: T) -> bool:
        if self._trigger in selection and (self._items & set(selection)):
            raise ValidationError(
                f"If '{self._trigger}' is selected, none of {self._items} can be selected."
            )
        return True


class AtLeastN(BaseRule[T]):
    def __init__(self, n: int):
        super().__init__()
        self._n = n

    def validate(self, *selection: T) -> bool:
        if len(self._items & set(selection)) < self._n:
            raise ValidationError(
                f"At least {self._n} of {self._items} must be selected."
            )
        return True


class NotAll(BaseRule[T]):
    def validate(self, *selection: T) -> bool:
        if (self._items & set(selection)) == self._items:
            raise ValidationError(f"Cannot select all of {self._items}.")
        return True
