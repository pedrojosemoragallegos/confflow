from datetime import datetime
from typing import TypeAlias, Union

# Primitive Field Value Aliases
Number: TypeAlias = Union[int, float]
Primitive: TypeAlias = Union[str, Number, bool, None, datetime, bytes]

StringFieldValue: TypeAlias = str
IntegerFieldValue: TypeAlias = int
FloatFieldValue: TypeAlias = float
BooleanFieldValue: TypeAlias = bool
TimestampFieldValue: TypeAlias = datetime
BytesFieldValue: TypeAlias = bytes


# Structured Field Value Aliases
ListFieldValue: TypeAlias = list[Primitive]
MappingFieldValue: TypeAlias = dict[str, Primitive]
SetFieldValue: TypeAlias = set[Primitive]

FieldStructured: TypeAlias = Union[
    Primitive,
    ListFieldValue,
    MappingFieldValue,
    SetFieldValue,
]

# General field value
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
