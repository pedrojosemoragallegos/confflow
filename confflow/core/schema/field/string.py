from typing import Optional

from ...constraint import (
    Constraint,
    EnumValues,
    MaxLength,
    MinLength,
    Regex,
)
from .field import Field


class StringField(Field[str]):
    def __init__(
        self,
        name: str,
        description: str,
        *,
        default_value: Optional[str] = None,
        required: bool = False,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        regex: Optional[str] = None,
        enum: Optional[list[str]] = None,
    ):
        constraints: list[Constraint[str]] = []

        if min_length:
            constraints.append(MinLength(min_length))
        if max_length:
            constraints.append(MaxLength(max_length))
        if regex:
            constraints.append(Regex(regex))
        if enum:
            constraints.append(EnumValues(enum))

        super().__init__(
            name=name,
            description=description,
            default_value=default_value,
            required=required,
            constraints=constraints,
        )
