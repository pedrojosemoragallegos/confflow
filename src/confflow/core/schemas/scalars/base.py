from __future__ import annotations

from typing import TYPE_CHECKING, Final, Generic, TypeVar

from typing_extensions import override

from confflow.core.definitions.exceptions import DefinitionError
from confflow.core.schemas.base import Schema
from confflow.core.schemas.exceptions import SchemaError
from confflow.core.types import Value as ScalarValue

if TYPE_CHECKING:
    from confflow.core.definitions import Definition

Value = TypeVar(name="Value", bound=ScalarValue)


class Scalar(Schema, Generic[Value]):
    __slots__ = ("__default", "__definition")

    def __init__(
        self,
        name: str,
        description: str | None,
        /,
        *,
        optional: bool,
        definition: Definition[Value],
        default: Value | None = None,
    ) -> None:
        super().__init__(name, description, optional=optional)

        if default is not None:
            try:
                definition.validate(default)
            except DefinitionError as error:
                raise SchemaError(
                    "field default does not satisfy its definition"
                ) from error

        self.__definition: Final[Definition[Value]] = definition
        self.__default: Final[Value | None] = default

    @property
    def definition(self) -> Definition[Value]:
        return self.__definition

    @property
    def default(self) -> Value | None:
        return self.__default

    @override
    def validate(self, value: object, /) -> None:
        self.__definition.validate(value)

    @override
    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}(name={self.name!r}, "
            f"description={self.description!r}, optional={self.optional!r}, "
            f"definition={self.__definition!r}, default={self.__default!r})"
        )
