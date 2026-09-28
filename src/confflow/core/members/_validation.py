from __future__ import annotations

from ..exceptions import SchemaError


def _validate_collection_bounds(
    minimum: int | None, maximum: int | None, label: str
) -> None:
    if minimum is not None and (type(minimum) is not int or minimum < 0):
        raise SchemaError(f"{label} minimum must be a non-negative integer")
    if maximum is not None and (type(maximum) is not int or maximum < 0):
        raise SchemaError(f"{label} maximum must be a non-negative integer")
    if minimum is not None and maximum is not None and minimum > maximum:
        raise SchemaError(f"{label} minimum cannot exceed maximum")
