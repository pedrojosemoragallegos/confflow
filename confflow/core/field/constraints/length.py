# TODO do they all apply on sequence if yes rename the file!
from confflow.protocols import Constraint, HasLen


class MinLength(Constraint[HasLen]):
    def __init__(self, min_len: int) -> None:
        self.min_len = min_len

    def __call__(self, value: HasLen) -> None:
        if len(value) < self.min_len:
            raise ValueError(f"Length {len(value)} is less than minimum {self.min_len}")


class MaxLength(Constraint[HasLen]):
    def __init__(self, max_len: int) -> None:
        self.max_len = max_len

    def __call__(self, value: HasLen) -> None:
        if len(value) > self.max_len:
            raise ValueError(f"Length {len(value)} exceeds maximum {self.max_len}")


class ExactLength(Constraint[HasLen]):
    def __init__(self, exact_len: int) -> None:
        self.exact_len = exact_len

    def __call__(self, value: HasLen) -> None:
        if len(value) != self.exact_len:
            raise ValueError(
                f"Length {len(value)} is not equal to required {self.exact_len}"
            )


class LengthInRange(Constraint[HasLen]):
    def __init__(self, min_len: int, max_len: int) -> None:
        self.min_len = min_len
        self.max_len = max_len

    def __call__(self, value: HasLen) -> None:
        l = len(value)
        if l < self.min_len or l > self.max_len:
            raise ValueError(
                f"Length {l} not in range [{self.min_len}, {self.max_len}]"
            )


class NonEmpty(Constraint[HasLen]):
    def __call__(self, value: HasLen) -> None:
        if len(value) == 0:
            raise ValueError("Value must not be empty")


class Empty(Constraint[HasLen]):
    def __call__(self, value: HasLen) -> None:
        if len(value) != 0:
            raise ValueError("Value must be empty")


class LengthNotEqual(Constraint[HasLen]):
    def __init__(self, disallowed_len: int) -> None:
        self.disallowed_len = disallowed_len

    def __call__(self, value: HasLen) -> None:
        if len(value) == self.disallowed_len:
            raise ValueError(f"Length must not be {self.disallowed_len}")


class LengthMultipleOf(Constraint[HasLen]):
    def __init__(self, modulus: int) -> None:
        self.modulus = modulus

    def __call__(self, value: HasLen) -> None:
        if len(value) % self.modulus != 0:
            raise ValueError(f"Length {len(value)} is not a multiple of {self.modulus}")


class IsEmpty(Constraint[HasLen]):
    def __call__(self, value: HasLen) -> None:
        if len(value) != 0:
            raise ValueError("Value must be empty")


class IsNonEmpty(Constraint[HasLen]):
    def __call__(self, value: HasLen) -> None:
        if len(value) == 0:
            raise ValueError("Value must not be empty")


# TODO
# AllMatch[T] – validate every element using another constraint
# AnyMatch[T]
# NoneMatch[T]
# IsSorted[T]
# EndsWith[T]
# StartsWith[T] – matches first N elements
# EndsWith[T] – matches last N elements
# ContainsAt[T](index: int, expected: T)
# IsSorted[T] – optionally pass a key or reverse flag
# HasDuplicates[T]
# IsUnique[T]
