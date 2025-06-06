from datetime import datetime
from typing import (
    Optional,
    Sequence,
    Union,
    overload,
)

from .field_constraint import FieldConstraint
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
)

@overload
def Field(
    value: bool,
    *,
    name: str,
    description: Optional[str] = ...,
    constraints: Optional[Sequence[FieldConstraint[bool]]] = ...,
) -> BooleanField: ...
@overload
def Field(
    value: bytes,
    *,
    name: str,
    description: Optional[str] = ...,
    constraints: Optional[Sequence[FieldConstraint[bytes]]] = ...,
) -> BytesField: ...
@overload
def Field(
    value: dict,
    *,
    name: str,
    description: Optional[str] = ...,
    constraints: Optional[Sequence[FieldConstraint[dict]]] = ...,
) -> MappingField: ...
@overload
def Field(
    value: int,
    *,
    name: str,
    description: Optional[str] = ...,
    constraints: Optional[Sequence[FieldConstraint[int]]] = ...,
) -> IntegerField: ...
@overload
def Field(
    value: float,
    *,
    name: str,
    description: Optional[str] = ...,
    constraints: Optional[Sequence[FieldConstraint[float]]] = ...,
) -> FloatField: ...
@overload
def Field(
    value: list,
    *,
    name: str,
    description: Optional[str] = ...,
    constraints: Optional[Sequence[FieldConstraint[list]]] = ...,
) -> ListField: ...
@overload
def Field(
    value: set,
    *,
    name: str,
    description: Optional[str] = ...,
    constraints: Optional[Sequence[FieldConstraint[set]]] = ...,
) -> SetField: ...
@overload
def Field(
    value: str,
    *,
    name: str,
    description: Optional[str] = ...,
    constraints: Optional[Sequence[FieldConstraint[str]]] = ...,
) -> StringField: ...
@overload
def Field(
    value: Union[str, datetime],
    *,
    name: str,
    description: Optional[str] = ...,
    constraints: Optional[Sequence[FieldConstraint[Union[str, datetime]]]] = ...,
) -> TimestampField: ...
