from __future__ import annotations

from datetime import time
from typing import ClassVar

from .base import Literal


class LocalTimeLiteral(Literal[time]):
    __slots__ = ()

    VALUE_TYPE: ClassVar[type[time]] = time
