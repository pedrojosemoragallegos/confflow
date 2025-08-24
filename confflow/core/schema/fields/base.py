from datetime import datetime
from typing import Optional

from ...constraints import (
    AllItemsMatch,
    Constraint,
    EnumValues,
    GreaterThan,
    GreaterThanOrEqual,
    LessThan,
    LessThanOrEqual,
    MaxItems,
    MaxLength,
    MinItems,
    MinLength,
    Regex,
    UniqueItems,
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


class IntegerField(Field[int]):
    def __init__(
        self,
        name: str,
        description: str,
        *,
        default_value: Optional[int] = None,
        required: bool = False,
        gt: Optional[int] = None,
        ge: Optional[int] = None,
        lt: Optional[int] = None,
        le: Optional[int] = None,
    ):
        constraints: list[Constraint[int]] = []

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


class FloatListField(Field[list[float]]):
    def __init__(
        self,
        name: str,
        description: str,
        default_value: Optional[list[float]] = None,
        required: bool = False,
        min_items: Optional[int] = None,
        max_items: Optional[int] = None,
        unique_items: Optional[bool] = None,
        gt: Optional[float] = None,
        ge: Optional[float] = None,
        lt: Optional[float] = None,
        le: Optional[float] = None,
    ):
        constraints = []  # TODO typing

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


class DateField(Field[datetime]):
    def __init__(
        self,
        name: str,
        description: str,
        *,
        default_value: Optional[datetime] = None,
        required: bool = False,
    ):
        super().__init__(
            name=name,
            description=description,
            default_value=default_value,
            required=required,
            constraints=[],
        )


class DateListField(Field[list[datetime]]):
    def __init__(
        self,
        name: str,
        description: str,
        default_value: Optional[list[datetime]] = None,
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


class BytesField(Field[bytes]):
    def __init__(
        self,
        name: str,
        description: str,
        *,
        default_value: Optional[bytes] = None,
        required: bool = False,
    ):
        super().__init__(
            name=name,
            description=description,
            default_value=default_value,
            required=required,
            constraints=[],
        )


class BooleanListField(Field[list[bool]]):
    def __init__(
        self,
        name: str,
        description: str,
        default_value: Optional[list[bool]] = None,
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


class BooleanField(Field[bool]):
    def __init__(
        self,
        name: str,
        description: str,
        *,
        default_value: Optional[bool] = None,
        required: bool = False,
    ):
        super().__init__(
            name=name,
            description=description,
            default_value=default_value,
            required=required,
            constraints=[],
        )


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
