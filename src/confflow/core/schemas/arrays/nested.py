from __future__ import annotations

from typing import Final, Generic, TypeVar

from typing_extensions import override

from .base import Array

ItemT = TypeVar(name="ItemT")


class Nested(Array[list[ItemT]], Generic[ItemT]):
    __slots__ = ("__array",)

    def __init__(
        self,
        name: str,
        description: str | None,
        /,
        *,
        optional: bool = False,
        array: Array[ItemT],
    ) -> None:
        super().__init__(name, description, optional=optional)

        self.__array: Final[Array[ItemT]] = array

    @property
    def array(self) -> Array[ItemT]:
        return self.__array

    @override
    def _validate_item(self, value: list[ItemT], /) -> None:
        self.__array.validate(value)

    @override
    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}("
            f"name={self.name!r}, "
            f"description={self.description!r}, "
            f"optional={self.optional!r}, "
            f"array={self.__array!r})"
        )
