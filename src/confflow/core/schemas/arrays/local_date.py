from __future__ import annotations

from typing import Final

from typing_extensions import override

from confflow.core.definitions.time import LocalDate as LocalDateDefinition

from .base import Array


class LocalDate(Array):
    __slots__ = ("__definition",)

    def __init__(
        self, name: str, description: str | None = None, /, *, optional: bool = False
    ) -> None:
        super().__init__(name, description, optional=optional)

        self.__definition: Final[LocalDateDefinition] = LocalDateDefinition()

    @property
    def definition(self) -> LocalDateDefinition:
        return self.__definition

    @override
    def _validate_item(self, value: object, /) -> None:
        self.__definition.validate(value)
