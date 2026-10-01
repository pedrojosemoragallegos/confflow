from __future__ import annotations

from typing import Final

from typing_extensions import override

from confflow.core.definitions import Float as FloatDefinition

from .base import Array


class Float(Array):
    __slots__ = ("__definition",)

    def __init__(
        self,
        name: str,
        description: str | None = None,
        /,
        *,
        optional: bool = False,
        minimum: float | None = None,
        maximum: float | None = None,
    ) -> None:
        super().__init__(name, description, optional=optional)

        self.__definition: Final[FloatDefinition] = FloatDefinition(
            minimum=minimum, maximum=maximum
        )

    @property
    def definition(self) -> FloatDefinition:
        return self.__definition

    @override
    def _validate_item(self, value: object, /) -> None:
        self.__definition.validate(value)
