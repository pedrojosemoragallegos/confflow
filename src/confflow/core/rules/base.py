from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Collection

    from ..members.base import Entry


class Rule(ABC):
    __slots__ = ()

    @property
    @abstractmethod
    def members(self) -> tuple[Entry, ...]:
        raise NotImplementedError

    @abstractmethod
    def validate(
        self, present_members: Collection[Entry], path: tuple[str | int, ...]
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def __repr__(self) -> str:
        raise NotImplementedError
