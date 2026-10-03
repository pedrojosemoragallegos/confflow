from __future__ import annotations

from typing import TYPE_CHECKING, Final, final

from typing_extensions import override

from confflow.core.definitions import Float as FloatDefinition

from .base import Array

if TYPE_CHECKING:
    from confflow.core.definitions.constraints import Constraint


@final
class Float(Array[float]):
    __slots__ = ("__definition",)

    def __init__(
        self,
        name: str,
        description: str | None,
        /,
        *constraints: Constraint[float],
        optional: bool = False,
        minimum: float | None = None,
        maximum: float | None = None,
    ) -> None:
        super().__init__(name, description, optional=optional)

        self.__definition: Final[FloatDefinition] = FloatDefinition(
            *constraints, minimum=minimum, maximum=maximum
        )

    @property
    def definition(self) -> FloatDefinition:
        return self.__definition

    @override
    def _validate_item(self, value: float, /) -> None:
        self.__definition.validate(value)
