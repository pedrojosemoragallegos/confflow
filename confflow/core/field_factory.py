from datetime import datetime
from typing import (
    Any,
    Optional,
    Sequence,
    TypeAlias,
    Union,
)

from .field_constraint import FieldConstraint
from .field_values import (
    BooleanFieldValue,
    BytesFieldValue,
    FieldValue,
    FloatFieldValue,
    IntegerFieldValue,
    StringFieldValue,
)
from .fields import (
    BooleanField,
    BytesField,
    FloatField,
    IntegerField,
    ListField,
    MappingField,
    SetField,
    StringField,
    TimestampField,
    TimestampFieldValue,
)

FieldType: TypeAlias = Union[
    BooleanField,
    BytesField,
    MappingField,
    FloatField,
    IntegerField,
    ListField,
    SetField,
    StringField,
    TimestampField,
]


def map_to_fieldtype(value: FieldValue) -> type[FieldType]:
    if isinstance(value, StringFieldValue):
        return StringField
    elif isinstance(value, IntegerFieldValue):
        return IntegerField
    elif isinstance(value, FloatFieldValue):
        return FloatField
    elif isinstance(value, BooleanFieldValue):
        return BooleanField
    elif isinstance(value, TimestampFieldValue):
        return TimestampField
    elif isinstance(value, BytesFieldValue):
        return BytesField
    elif isinstance(value, list) and all(
        isinstance(
            item,
            (str, int, float, bool, datetime, bytes),
        )
        for item in value
    ):
        return ListField
    elif isinstance(value, dict) and all(
        isinstance(
            item,
            (str, int, float, bool, datetime, bytes),
        )
        for item in value
    ):
        return MappingField
    elif isinstance(value, set) and all(
        isinstance(
            item,
            (str, int, float, bool, datetime, bytes),
        )
        for item in value
    ):
        return SetField
    else:
        raise TypeError(
            f"No matching field type for value: {value} (type: {type(value)})"
        )


def Field(
    value: FieldValue,
    *,
    name: str,
    description: Optional[str] = None,
    constraints: Optional[Sequence[FieldConstraint[Any]]] = None,
) -> FieldType:
    return map_to_fieldtype(value)(
        value=value,
        name=name,
        description=description,
        constraints=constraints,
    )
