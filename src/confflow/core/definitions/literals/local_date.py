from __future__ import annotations

from datetime import date
from typing import ClassVar

from .base import Literal


class LocalDateLiteral(Literal[date]):
    __slots__ = ()

    VALUE_TYPE: ClassVar[type[date]] = date
