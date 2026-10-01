from __future__ import annotations

from abc import abstractmethod
from typing import Generic, TypeVar

from typing_extensions import override

from confflow.core.schemas.base import Schema

ItemT = TypeVar(name="ItemT")


class Array(Schema[list[ItemT]], Generic[ItemT]):
    @override
    def validate(self, value: list[ItemT], /) -> None:
        for item in value:
            self._validate_item(item)

    @abstractmethod
    def _validate_item(self, value: ItemT, /) -> None: ...

    @override
    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}("
            f"name={self.name!r}, "
            f"description={self.description!r}, "
            f"optional={self.optional!r})"
        )
