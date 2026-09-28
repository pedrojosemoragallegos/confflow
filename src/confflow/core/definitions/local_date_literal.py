from __future__ import annotations

from datetime import date
from typing import ClassVar

from .literal import Literal


class LocalDateLiteral(Literal[date]):
    __slots__ = ()

    _EXPECTED_TYPE: ClassVar[type[object] | None] = date
