from typing import Optional

from ...constraint import (
    AllItemsMatch,
    Constraint,
    GreaterThan,
    GreaterThanOrEqual,
    LessThan,
    LessThanOrEqual,
    MaxItems,
    MinItems,
    UniqueItems,
)
from .field import Field


class IntegerListField(Field[list[int]]):
    def __init__(
        self,
        name: str,
        description: str,
        *,
        default_value: Optional[list[int]] = None,
        required: bool = False,
        min_items: Optional[int] = None,
        max_items: Optional[int] = None,
        unique_items: Optional[bool] = None,
        gt: Optional[int] = None,
        ge: Optional[int] = None,
        lt: Optional[int] = None,
        le: Optional[int] = None,
    ):
        constraints: list[Constraint[str]] = []

        if min_items is not None:
            constraints.append(MinItems(min_items))
        if max_items is not None:
            constraints.append(MaxItems(max_items))
        if unique_items:
            constraints.append(UniqueItems())

        item_constraints = []  # TODO typing

        if gt is not None:
            item_constraints.append(GreaterThan(gt))
        if ge is not None:
            item_constraints.append(GreaterThanOrEqual(ge))
        if lt is not None:
            item_constraints.append(LessThan(lt))
        if le is not None:
            item_constraints.append(LessThanOrEqual(le))

        if item_constraints:
            constraints.append(AllItemsMatch(item_constraints))

        super().__init__(
            name=name,
            description=description,
            default_value=default_value,
            required=required,
            constraints=constraints,
        )
