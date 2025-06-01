from confflow.protocols import Constraint
from confflow.types import ValueTypes


class Contains(Constraint[set[ValueTypes]]):
    def __init__(self, item: ValueTypes) -> None:
        self.item = item

    def __call__(self, value: set[ValueTypes]) -> None:
        if self.item not in value:
            raise ValueError(f"set must contain item: {self.item}")


class NotContains(Constraint[set[ValueTypes]]):
    def __init__(self, item: ValueTypes) -> None:
        self.item = item

    def __call__(self, value: set[ValueTypes]) -> None:
        if self.item in value:
            raise ValueError(f"set must not contain item: {self.item}")


class ContainsAll(Constraint[set[ValueTypes]]):
    def __init__(self, required: set[ValueTypes]) -> None:
        self.required = required

    def __call__(self, value: set[ValueTypes]) -> None:
        if not self.required.issubset(value):
            missing = self.required - value
            raise ValueError(f"set is missing required items: {missing}")


class IsSubsetOf(Constraint[set[ValueTypes]]):
    def __init__(self, superset: set[ValueTypes]) -> None:
        self.superset = superset

    def __call__(self, value: set[ValueTypes]) -> None:
        if not value.issubset(self.superset):
            raise ValueError(f"set is not a subset of {self.superset}")


class IsSupersetOf(Constraint[set[ValueTypes]]):
    def __init__(self, subset: set[ValueTypes]) -> None:
        self.subset = subset

    def __call__(self, value: set[ValueTypes]) -> None:
        if not value.issuperset(self.subset):
            raise ValueError(f"set is not a superset of {self.subset}")


class IsDisjointWith(Constraint[set[ValueTypes]]):
    def __init__(self, other: set[ValueTypes]) -> None:
        self.other = other

    def __call__(self, value: set[ValueTypes]) -> None:
        if not value.isdisjoint(self.other):
            raise ValueError(f"set must be disjoint with {self.other}")


class Equals(Constraint[set[ValueTypes]]):
    def __init__(self, expected: set[ValueTypes]) -> None:
        self.expected = expected

    def __call__(self, value: set[ValueTypes]) -> None:
        if value != self.expected:
            raise ValueError(f"set must exactly match {self.expected}")
