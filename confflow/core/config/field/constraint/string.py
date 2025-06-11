import re
from typing import TypeVar

from .constraint import Constraint

T = TypeVar("T")


class IsAlpha(Constraint[str]):
    def __call__(self, value: str) -> None:
        if not value.isalpha():
            raise ValueError("String must contain only alphabetic characters.")


class IsDigit(Constraint[str]):
    def __call__(self, value: str) -> None:
        if not value.isdigit():
            raise ValueError("String must contain only digits.")


class IsAlnum(Constraint[str]):
    def __call__(self, value: str) -> None:
        if not value.isalnum():
            raise ValueError("String must contain only alphanumeric characters.")


class IsLower(Constraint[str]):
    def __call__(self, value: str) -> None:
        if not value.islower():
            raise ValueError("String must be lowercase.")


class IsUpper(Constraint[str]):
    def __call__(self, value: str) -> None:
        if not value.isupper():
            raise ValueError("String must be uppercase.")


class IsTitle(Constraint[str]):
    def __call__(self, value: str) -> None:
        if not value.istitle():
            raise ValueError("String must be title-cased.")


class IsPrintable(Constraint[str]):
    def __call__(self, value: str) -> None:
        if not value.isprintable():
            raise ValueError("String must contain only printable characters.")


class IsAscii(Constraint[str]):
    def __call__(self, value: str) -> None:
        if not all(ord(c) < 128 for c in value):
            raise ValueError("String must contain only ASCII characters.")


class MatchesRegex(Constraint[str]):
    def __init__(self, pattern: str) -> None:
        self.regex = re.compile(pattern)

    def __call__(self, value: str) -> None:
        if not self.regex.fullmatch(value):
            raise ValueError(
                f"String does not match regex pattern: {self.regex.pattern}."
            )


class StartsWith(Constraint[str]):
    def __init__(self, prefix: str) -> None:
        self.prefix = prefix

    def __call__(self, value: str) -> None:
        if not value.startswith(self.prefix):
            raise ValueError(f"String must start with '{self.prefix}'.")


class EndsWith(Constraint[str]):
    def __init__(self, suffix: str) -> None:
        self.suffix = suffix

    def __call__(self, value: str) -> None:
        if not value.endswith(self.suffix):
            raise ValueError(f"String must end with '{self.suffix}'.")


class ContainsSubstring(Constraint[str]):
    def __init__(self, substring: str) -> None:
        self.substring = substring

    def __call__(self, value: str) -> None:
        if self.substring not in value:
            raise ValueError(f"String must contain '{self.substring}'.")
