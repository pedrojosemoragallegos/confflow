from __future__ import annotations

from datetime import datetime
from typing import Union

NumberLike = Union[int, float]
PrimitiveValue = Union[str, NumberLike, bool, None, datetime, bytes]

StructuredValues = Union[
    PrimitiveValue,
    list[PrimitiveValue],
    dict[str, PrimitiveValue],
    set[PrimitiveValue],
]
