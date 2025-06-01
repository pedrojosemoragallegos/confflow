from __future__ import annotations

from datetime import datetime
from typing import Union

Numerical = Union[int, float]
Scalar = Union[str, Numerical, bool, None, datetime, bytes]

ValueTypes = Union[
    Scalar,
    list[Scalar],
    dict[str, Scalar],
    set[Scalar],
]
