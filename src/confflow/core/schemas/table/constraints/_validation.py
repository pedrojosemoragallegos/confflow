from __future__ import annotations

from confflow.core.errors import SchemaError


def validate_names(fields: tuple[str, ...], /) -> None:
    if any(not isinstance(field, str) for field in fields):
        raise SchemaError("table constraint operands must be child names")


def validate_fields(fields: tuple[str, ...], /, *, minimum: int = 2) -> None:
    if len(fields) < minimum:
        count = "one field is" if minimum == 1 else "two fields are"
        raise SchemaError(f"at least {count} required")
    validate_names(fields)
    if len(set(fields)) != len(fields):
        raise SchemaError("fields must be unique")
