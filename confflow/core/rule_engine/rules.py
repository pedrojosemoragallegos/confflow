from typing import TypeAlias

from ...common.types import Schema
from .._rules import (
    AllOrNone as _AllOrNone,
    AtLeastN as _AtLeastN,
    BaseRule as _BaseRule,
    ExactlyN as _ExactlyN,
    Excludes as _Excludes,
    MutuallyExclusive as _MutuallyExclusive,
    NotAll as _NotAll,
    OneOfGroup as _OneOfGroup,
    RequiresAll as _RequiresAll,
    RequiresOneOf as _RequiresOneOf,
)

AllOrNone: TypeAlias = _AllOrNone[Schema]
AtLeastN: TypeAlias = _AtLeastN[Schema]
BaseRule: TypeAlias = _BaseRule[Schema]
ExactlyN: TypeAlias = _ExactlyN[Schema]
Excludes: TypeAlias = _Excludes[Schema]
MutuallyExclusive: TypeAlias = _MutuallyExclusive[Schema]
NotAll: TypeAlias = _NotAll[Schema]
OneOfGroup: TypeAlias = _OneOfGroup[Schema]
RequiresAll: TypeAlias = _RequiresAll[Schema]
RequiresOneOf: TypeAlias = _RequiresOneOf[Schema]
