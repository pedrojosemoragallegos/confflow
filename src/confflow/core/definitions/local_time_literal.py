from __future__ import annotations

from datetime import time
from typing import ClassVar

from .literal import Literal


class LocalTimeLiteral(Literal[time]):
    __slots__ = ()

    _EXPECTED_TYPE: ClassVar[type[object] | None] = time
