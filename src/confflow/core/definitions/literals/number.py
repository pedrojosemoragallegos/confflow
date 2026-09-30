from __future__ import annotations

from typing import ClassVar

from .base import Literal


class NumberLiteral(Literal[int]):
    __slots__ = ()

    VALUE_TYPE: ClassVar[type[int]] = int
