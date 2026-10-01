from __future__ import annotations

from re import Pattern, compile as compile_pattern
from typing import Final

from .exceptions import SchemaError

_NAME_PATTERN: Final[Pattern[str]] = compile_pattern(pattern=r"[A-Za-z0-9_-]+")


def validate_name(label: str, /, *, value: object) -> None:
    if type(value) is not str or _NAME_PATTERN.fullmatch(string=value) is None:
        raise SchemaError(
            f"{label} must contain only ASCII letters, digits, '_' or '-'"
        )
