from __future__ import annotations

from datetime import datetime
from typing import Iterable, Optional, Union, final

from confflow.core.field import (
    BoolField,
    BytesField,
    DictField,
    FloatField,
    IntField,
    ListField,
    SetField,
    StrField,
    TimestampField,
)
from confflow.core.field.constraints import Constraint
from confflow.types import ValueTypes

FieldTypes = Union[
    IntField,
    FloatField,
    BoolField,
    StrField,
    TimestampField,
    BytesField,
    ListField,
    DictField,
    SetField,
]


@final
class Config:
    def __init__(self, name: str, description: str = ""):
        self._name: str = name
        self._description: str = description
        self._fields: list[FieldTypes] = []  # TODO ordered set?

    def addField(
        self,
        name: str,
        *,
        description: str = "",
        value: ValueTypes,
        default_value: Optional[ValueTypes] = None,
        required: bool = False,
        constraints: Optional[Iterable[Constraint[ValueTypes]]] = None,
    ) -> Config:
        if isinstance(value, int):
            field = IntField
        elif isinstance(value, float):
            field = FloatField
        elif isinstance(value, str):
            field = StrField
        elif isinstance(value, datetime):
            field = TimestampField
        elif isinstance(value, bytes):
            field = BytesField
        elif isinstance(value, list):
            field = ListField
        elif isinstance(value, dict):
            field = DictField
        elif isinstance(value, set):
            field = SetField
        elif isinstance(value, bool):
            field = BoolField
        else:
            raise TypeError(f"Unsupported type for value: {type(value).__name__}")

        self._fields.append(
            field(
                name=name,
                description=description,
                value=value,
                default_value=default_value,
                required=required,
                constraints=constraints,
            )
        )

        return self

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"name={self._name!r}, "
            f"description={self._description!r}, "
            f"fields={[field for field in self._fields]!r})"
        )
