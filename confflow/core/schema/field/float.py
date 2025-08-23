from typing import Optional

from ...constraint import (
    Constraint,
    GreaterThan,
    GreaterThanOrEqual,
    LessThan,
    LessThanOrEqual,
)
from .field import Field


class FloatField(Field[float]):
    def __init__(
        self,
        name: str,
        description: str,
        *,
        default_value: Optional[float] = None,
        required: bool = False,
        gt: Optional[float] = None,
        ge: Optional[float] = None,
        lt: Optional[float] = None,
        le: Optional[float] = None,
    ):
        constraints: list[Constraint[float]] = []

        if gt:
            constraints.append(GreaterThan(gt))
        if ge:
            constraints.append(GreaterThanOrEqual(ge))
        if lt:
            constraints.append(LessThan(lt))
        if le:
            constraints.append(LessThanOrEqual(le))

        super().__init__(
            name=name,
            description=description,
            default_value=default_value,
            required=required,
            constraints=constraints,
        )
