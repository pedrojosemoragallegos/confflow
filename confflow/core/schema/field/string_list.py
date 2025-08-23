from typing import Optional

from ...constraint import (
    AllItemsMatch,
    Constraint,
    EnumValues,
    MaxItems,
    MaxLength,
    MinItems,
    MinLength,
    Regex,
    UniqueItems,
)
from .field import Field


class StringListField(Field[list[str]]):
    def __init__(
        self,
        name: str,
        description: str,
        *,
        default_value: Optional[list[str]] = None,
        required: bool = False,
        min_items: Optional[int] = None,
        max_items: Optional[int] = None,
        unique_items: Optional[bool] = None,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        regex: Optional[str] = None,
        enum: Optional[list[str]] = None,
    ):
        constraints: list[Constraint[str]] = []

        if min_items is not None:
            constraints.append(MinItems(min_items))
        if max_items is not None:
            constraints.append(MaxItems(max_items))
        if unique_items:
            constraints.append(UniqueItems())

        item_constraints = []  # TODO typing

        if min_length is not None:
            item_constraints.append(MinLength(min_length))
        if max_length is not None:
            item_constraints.append(MaxLength(max_length))
        if regex is not None:
            item_constraints.append(Regex(regex))
        if enum is not None:
            item_constraints.append(EnumValues(enum))

        if item_constraints:
            constraints.append(AllItemsMatch(item_constraints))

        super().__init__(
            name=name,
            description=description,
            default_value=default_value,
            required=required,
            constraints=constraints,
        )
