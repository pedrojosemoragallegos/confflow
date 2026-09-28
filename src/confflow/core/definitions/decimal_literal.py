from __future__ import annotations

from typing import ClassVar

from .literal import Literal


class DecimalLiteral(Literal[float]):
    __slots__ = ()

    _EXPECTED_TYPE: ClassVar[type[object] | None] = float
