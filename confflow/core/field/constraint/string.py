import re
from typing import TypeVar

from confflow.core.types import (
    StringFieldValue,
)

from .constraint import BaseConstraint

T = TypeVar("T")


class IsAlpha(BaseConstraint[StringFieldValue]):
    def __call__(self, value: StringFieldValue) -> None:
        if not value.isalpha():
            raise ValueError("String must contain only alphabetic characters.")


class IsDigit(BaseConstraint[StringFieldValue]):
    def __call__(self, value: StringFieldValue) -> None:
        if not value.isdigit():
            raise ValueError("String must contain only digits.")


class IsAlnum(BaseConstraint[StringFieldValue]):
    def __call__(self, value: StringFieldValue) -> None:
        if not value.isalnum():
            raise ValueError("String must contain only alphanumeric characters.")


class IsLower(BaseConstraint[StringFieldValue]):
    def __call__(self, value: StringFieldValue) -> None:
        if not value.islower():
            raise ValueError("String must be lowercase.")


class IsUpper(BaseConstraint[StringFieldValue]):
    def __call__(self, value: StringFieldValue) -> None:
        if not value.isupper():
            raise ValueError("String must be uppercase.")


class IsTitle(BaseConstraint[StringFieldValue]):
    def __call__(self, value: StringFieldValue) -> None:
        if not value.istitle():
            raise ValueError("String must be title-cased.")


class IsPrintable(BaseConstraint[StringFieldValue]):
    def __call__(self, value: StringFieldValue) -> None:
        if not value.isprintable():
            raise ValueError("String must contain only printable characters.")


class IsAscii(BaseConstraint[StringFieldValue]):
    def __call__(self, value: StringFieldValue) -> None:
        if not all(ord(c) < 128 for c in value):
            raise ValueError("String must contain only ASCII characters.")


class MatchesRegex(BaseConstraint[StringFieldValue]):
    def __init__(self, pattern: str) -> None:
        self.regex = re.compile(pattern)

    def __call__(self, value: StringFieldValue) -> None:
        if not self.regex.fullmatch(value):
            raise ValueError(
                f"String does not match regex pattern: {self.regex.pattern}."
            )


class StartsWith(BaseConstraint[StringFieldValue]):
    def __init__(self, prefix: str) -> None:
        self.prefix = prefix

    def __call__(self, value: StringFieldValue) -> None:
        if not value.startswith(self.prefix):
            raise ValueError(f"String must start with '{self.prefix}'.")


class EndsWith(BaseConstraint[StringFieldValue]):
    def __init__(self, suffix: str) -> None:
        self.suffix = suffix

    def __call__(self, value: StringFieldValue) -> None:
        if not value.endswith(self.suffix):
            raise ValueError(f"String must end with '{self.suffix}'.")


class ContainsSubstring(BaseConstraint[StringFieldValue]):
    def __init__(self, substring: str) -> None:
        self.substring = substring

    def __call__(self, value: StringFieldValue) -> None:
        if self.substring not in value:
            raise ValueError(f"String must contain '{self.substring}'.")
