from datetime import datetime
from typing import TypeAlias, Union

from .field.field import BaseField

## Primitive Field Values
StringFieldValue: TypeAlias = str
IntegerFieldValue: TypeAlias = int
FloatFieldValue: TypeAlias = float
BooleanFieldValue: TypeAlias = bool
TimestampFieldValue: TypeAlias = datetime
BytesFieldValue: TypeAlias = bytes

NumberFieldValue: TypeAlias = Union[IntegerFieldValue, FloatFieldValue]
PrimitiveFieldValue: TypeAlias = Union[
    StringFieldValue,
    IntegerFieldValue,
    FloatFieldValue,
    BooleanFieldValue,
    TimestampFieldValue,
    BytesFieldValue,
]

## Structured Field Values
ListFieldValue: TypeAlias = list[PrimitiveFieldValue]
MappingFieldValue: TypeAlias = dict[StringFieldValue, PrimitiveFieldValue]
SetFieldValue: TypeAlias = set[PrimitiveFieldValue]

StructuredFieldValue: TypeAlias = Union[
    PrimitiveFieldValue,
    ListFieldValue,
    MappingFieldValue,
    SetFieldValue,
]

## General Field Value
FieldValue: TypeAlias = Union[
    StringFieldValue,
    IntegerFieldValue,
    FloatFieldValue,
    BooleanFieldValue,
    TimestampFieldValue,
    BytesFieldValue,
    ListFieldValue,
    MappingFieldValue,
    SetFieldValue,
]

## General Field Types
StringField: TypeAlias = BaseField[StringFieldValue]
IntegerField: TypeAlias = BaseField[IntegerFieldValue]
FloatField: TypeAlias = BaseField[FloatFieldValue]
BooleanField: TypeAlias = BaseField[BooleanFieldValue]
TimestampField: TypeAlias = BaseField[TimestampFieldValue]
BytesField: TypeAlias = BaseField[BytesFieldValue]
ListField: TypeAlias = BaseField[ListFieldValue]
MappingField: TypeAlias = BaseField[MappingFieldValue]
SetField: TypeAlias = BaseField[SetFieldValue]

## General Field Type
FieldType: TypeAlias = Union[
    StringField,
    IntegerFieldValue,
    FloatFieldValue,
    BooleanField,
    TimestampField,
    BytesField,
    ListField,
    MappingField,
    SetField,
]
