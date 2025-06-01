from __future__ import annotations

from datetime import datetime
from typing import Union

Scalar = Union[str, int, float, bool, None, datetime, bytes]

ValueTypes = Union[
    Scalar,
    list[Scalar],
    dict[str, Scalar],
    set[Scalar],
]
