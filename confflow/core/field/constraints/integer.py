from confflow.protocols import Constraint


class IsEven(Constraint[int]):
    def __call__(self, value: int) -> None:
        if value % 2 != 0:
            raise ValueError("Value must be even")


class IsOdd(Constraint[int]):
    def __call__(self, value: int) -> None:
        if value % 2 != 1:
            raise ValueError("Value must be odd")


class MultipleOf(Constraint[int]):
    def __init__(self, base: int) -> None:
        if base == 0:
            raise ValueError("Base must not be zero")
        self.base = base

    def __call__(self, value: int) -> None:
        if value % self.base != 0:
            raise ValueError(f"Value must be a multiple of {self.base}")


class Divides(Constraint[int]):
    def __init__(self, divisor: int) -> None:
        if divisor == 0:
            raise ValueError("Divisor must not be zero")
        self.divisor = divisor

    def __call__(self, value: int) -> None:
        if self.divisor % value != 0:
            raise ValueError(f"{value} does not divide {self.divisor}")


class IsPrime(Constraint[int]):
    def __call__(self, value: int) -> None:
        if value < 2:
            raise ValueError("Value must be a prime number")
        for i in range(2, int(value**0.5) + 1):
            if value % i == 0:
                raise ValueError("Value is not a prime number")


class IsPowerOfTwo(Constraint[int]):
    def __call__(self, value: int) -> None:
        if value <= 0 or (value & (value - 1)) != 0:
            raise ValueError("Value must be a power of two")


class IsNonNegativeInteger(Constraint[int]):
    def __call__(self, value: int) -> None:
        if value < 0:
            raise ValueError("Value must be a non-negative integer")
