from __future__ import annotations

from typing import Final

from typing_extensions import override

from confflow.core.definitions.time import (
    LocalDateTime as LocalDateTimeDefinition,
)

from .base import Array


class LocalDateTime(Array):
    __slots__ = ("__definition",)

    def __init__(
        self, name: str, description: str | None = None, /, *, optional: bool = False
    ) -> None:
        super().__init__(name, description, optional=optional)

        self.__definition: Final[LocalDateTimeDefinition] = LocalDateTimeDefinition()

    @property
    def definition(self) -> LocalDateTimeDefinition:
        return self.__definition

    @override
    def _validate_item(self, value: object, /) -> None:
        self.__definition.validate(value)
