from __future__ import annotations

from typing import Final, final

from typing_extensions import override

from confflow.core.definitions import Boolean as BooleanDefinition

from .base import Array


@final
class Boolean(Array[bool]):
    __slots__ = ("__definition",)

    def __init__(
        self, name: str, description: str | None, /, *, optional: bool = False
    ) -> None:
        super().__init__(name, description, optional=optional)

        self.__definition: Final[BooleanDefinition] = BooleanDefinition()

    @property
    def definition(self) -> BooleanDefinition:
        return self.__definition

    @override
    def _validate_item(self, value: bool, /) -> None:
        self.__definition.validate(value)
