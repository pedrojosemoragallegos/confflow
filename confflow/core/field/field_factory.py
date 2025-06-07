from typing import Iterable, Optional, Type, TypeVar

from confflow.core.field.constraint.constraint import BaseConstraint
from confflow.core.types import (
    BooleanField,
    BooleanFieldValue,
    BytesField,
    BytesFieldValue,
    FieldType,
    FieldValue,
    FloatField,
    FloatFieldValue,
    IntegerField,
    IntegerFieldValue,
    ListField,
    ListFieldValue,
    MappingField,
    MappingFieldValue,
    SetField,
    SetFieldValue,
    StringField,
    StringFieldValue,
    TimestampField,
    TimestampFieldValue,
)
from confflow.utils import recursive_is_instance

# from confflow.utils import is_valid_field_value

T = TypeVar("T", bound=FieldValue)


def FieldFactory(
    value: T,
    *,
    name: StringFieldValue,
    description: Optional[StringFieldValue] = None,
    constraints: Optional[Iterable[BaseConstraint[T]]] = None,
) -> FieldType:
    if recursive_is_instance(value, StringFieldValue):
        field_class: Type[StringField] = StringField
    elif recursive_is_instance(value, IntegerFieldValue):
        field_class: Type[IntegerField] = IntegerField
    elif recursive_is_instance(value, FloatFieldValue):
        field_class: Type[FloatField] = FloatField
    elif recursive_is_instance(value, BooleanFieldValue):
        field_class: Type[BooleanField] = BooleanField
    elif recursive_is_instance(value, TimestampFieldValue):
        field_class: Type[TimestampField] = TimestampField
    elif recursive_is_instance(value, BytesFieldValue):
        field_class: Type[BytesField] = BytesField
    elif recursive_is_instance(value, ListFieldValue):
        field_class: Type[ListFieldValue] = ListField
    elif recursive_is_instance(value, MappingFieldValue):
        field_class: Type[MappingFieldValue] = MappingField
    elif recursive_is_instance(value, SetFieldValue):
        field_class: Type[SetFieldValue] = SetField
    else:
        raise TypeError(
            f"No matching field type for value: {value} (type: {type(value)})"
        )

    return field_class(
        value=value, name=name, description=description, constraints=constraints
    )
