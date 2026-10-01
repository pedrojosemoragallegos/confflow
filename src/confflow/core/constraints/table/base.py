from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, ClassVar

if TYPE_CHECKING:
    from collections.abc import Mapping


class Constraint(ABC):
    __slots__ = ()

    NAME: ClassVar[str]

    @abstractmethod
    def __call__(self, value: Mapping[str, object], /) -> None: ...
