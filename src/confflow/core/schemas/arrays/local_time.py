from __future__ import annotations

from typing import Final

from typing_extensions import override

from confflow.core.definitions.time import LocalTime as LocalTimeDefinition

from .base import Array


class LocalTime(Array):
    __slots__ = ("__definition",)

    def __init__(
        self, name: str, description: str | None = None, /, *, optional: bool = False
    ) -> None:
        super().__init__(name, description, optional=optional)

        self.__definition: Final[LocalTimeDefinition] = LocalTimeDefinition()

    @property
    def definition(self) -> LocalTimeDefinition:
        return self.__definition

    @override
    def _validate_item(self, value: object, /) -> None:
        self.__definition.validate(value)
