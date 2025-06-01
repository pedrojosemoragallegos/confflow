from typing import TypeAlias

from .base_field import Field

StrField: TypeAlias = Field[str]
IntField: TypeAlias = Field[int]
FloatField: TypeAlias = Field[float]
BoolField: TypeAlias = Field[bool]
