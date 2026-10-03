from __future__ import annotations

from typing import TYPE_CHECKING, Final, Generic, TypeVar, final

from typing_extensions import override

from .base import Array

if TYPE_CHECKING:
    from confflow.core.errors import ValidationError

ItemT = TypeVar(name="ItemT")


@final
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
    def redact_error(self, error: ValidationError, value: object, /) -> None:
        if not isinstance(value, list):
            return
        for item in value:
            self.__array.redact_error(error, item)

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
