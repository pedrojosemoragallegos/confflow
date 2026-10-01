from __future__ import annotations

from typing import Final

from typing_extensions import override

from confflow.core.definitions import Integer as IntegerDefinition

from .base import Array


class Integer(Array):
    __slots__ = ("__definition",)

    def __init__(
        self,
        name: str,
        description: str | None = None,
        /,
        *,
        optional: bool = False,
        minimum: int | None = None,
        maximum: int | None = None,
    ) -> None:
        super().__init__(name, description, optional=optional)

        self.__definition: Final[IntegerDefinition] = IntegerDefinition(
            minimum=minimum, maximum=maximum
        )

    @property
    def definition(self) -> IntegerDefinition:
        return self.__definition

    @override
    def _validate_item(self, value: object, /) -> None:
        self.__definition.validate(value)
