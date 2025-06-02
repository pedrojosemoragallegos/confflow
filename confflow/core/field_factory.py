from typing import (
    Any,
    Final,
    Optional,
    Sequence,
    TypeAlias,
    Union,
)

from confflow.protocols import Constraint

from .field_values import (
    BooleanFieldValue,
    BytesFieldValue,
    FloatFieldValue,
    IntegerFieldValue,
    ListFieldValue,
    MappingFieldValue,
    SetFieldValue,
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

FieldType: Final[TypeAlias] = Union[
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


def _map_to_fieldtype(value: FieldValue) -> type[FieldType]:
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
    elif isinstance(value, ListFieldValue):
        return ListField
    elif isinstance(value, MappingFieldValue):
        return MappingField
    elif isinstance(value, SetFieldValue):
        return SetField
    else:
        raise TypeError(
            f"No matching field type for value: {value} (type: {type(value)})"
        )


def create_field(
    value: FieldValue,
    name: str,
    required: bool,
    description: Optional[str] = None,
    default_value: Optional[Any] = None,
    constraints: Optional[Sequence[Constraint[Any]]] = None,
) -> FieldType:
    return _map_to_fieldtype(value)(
        name=name,
        description=description,
        value=value,
        default_value=default_value,
        required=required,
        constraints=constraints,
    )
