from typing import Optional

from ...constraint import (
    MaxItems,
    MinItems,
    UniqueItems,
)
from .field import Field


class BytesListField(Field[list[bytes]]):
    def __init__(
        self,
        name: str,
        description: str,
        default_value: Optional[list[bytes]] = None,
        required: bool = False,
        min_items: Optional[int] = None,
        max_items: Optional[int] = None,
        unique_items: Optional[bool] = None,
    ):
        constraints = []  # TODO typing

        if min_items is not None:
            constraints.append(MinItems(min_items))
        if max_items is not None:
            constraints.append(MaxItems(max_items))
        if unique_items:
            constraints.append(UniqueItems())

        super().__init__(
            name=name,
            description=description,
            default_value=default_value,
            required=required,
            constraints=constraints,
        )
