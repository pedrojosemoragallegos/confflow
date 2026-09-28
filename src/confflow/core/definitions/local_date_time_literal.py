from __future__ import annotations

from datetime import datetime
from typing import ClassVar

from .literal import Literal


class LocalDateTimeLiteral(Literal[datetime]):
    __slots__ = ()

    _EXPECTED_TYPE: ClassVar[type[object] | None] = datetime
    _DATETIME_IS_AWARE: ClassVar[bool | None] = False
