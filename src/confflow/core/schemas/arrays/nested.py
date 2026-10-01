from __future__ import annotations

from typing import Final

from typing_extensions import override

from .base import Array


class Nested(Array):
    __slots__ = ("__array",)

    def __init__(
        self,
        name: str,
        description: str | None = None,
        /,
        *,
        optional: bool = False,
        array: Array,
    ) -> None:
        super().__init__(name, description, optional=optional)

        self.__array: Final[Array] = array

    @property
    def array(self) -> Array:
        return self.__array

    @override
    def _validate_item(self, value: object, /) -> None:
        self.__array.validate(value)

    @override
    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}(name={self.name!r}, "
            f"description={self.description!r}, "
            f"optional={self.optional!r}, "
            f"array={self.__array!r})"
        )
