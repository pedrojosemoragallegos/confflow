from datetime import datetime
from typing import Dict, List, Set, TypeAlias

from confflow.types import PrimitiveValue

from .base_field import Field

StrField: TypeAlias = Field[str]
IntField: TypeAlias = Field[int]
FloatField: TypeAlias = Field[float]
BoolField: TypeAlias = Field[bool]
TimestampField: TypeAlias = Field[datetime]
BytesField: TypeAlias = Field[bytes]
ListField: TypeAlias = Field[List[PrimitiveValue]]
DictField: TypeAlias = Field[Dict[str, PrimitiveValue]]
SetField: TypeAlias = Field[Set[PrimitiveValue]]
