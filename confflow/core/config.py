from __future__ import annotations

from collections import OrderedDict
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
from confflow.protocols import Constraint
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
        self._fields: OrderedDict[str, FieldTypes] = OrderedDict()

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
        if isinstance(value, bool):
            field = BoolField
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
        else:
            raise TypeError(f"Unsupported type for value: {type(value).__name__}")

        if name in self._fields:
            raise ValueError(f"Field with name '{name}' already exists.")

        self._fields[name] = field(
            name=name,
            description=description,
            value=value,
            default_value=default_value,
            required=required,
            constraints=constraints,
        )

        return self

    def keys(self):  # TODO add typing
        return self._fields.keys()

    def values(self):  # TODO add typing
        return self._fields.values()

    def items(self):  # TODO add typing
        return self._fields.items()

    def __getitem__(self, key: str) -> FieldTypes:
        return self._fields[key]

    def __contains__(self, key: str) -> bool:
        return key in self._fields

    def __iter__(self):  # TODO add typing
        return iter(self._fields)

    def __len__(self) -> int:
        return len(self._fields)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"name={self._name!r}, "
            f"description={self._description!r}, "
            f"fields={[field for field in self._fields.values()]!r})"
        )

    ## Only for iPython ## # TODO create a decorator or like this
    def _ipython_key_completions_(self):
        return list(self._fields.keys())
