from __future__ import annotations

from abc import abstractmethod
from typing import Final, Generic, TypeVar

from typing_extensions import override

from ...definitions.base import Definition, Value as ScalarValue
from ...definitions.exceptions import DefinitionError
from ...exceptions import SchemaError
from ..base import Entry

Value = TypeVar(name="Value", bound=ScalarValue)


class Scalar(Entry, Generic[Value]):
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

        # TODO: is this correct?
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

    def validate(self, value: object) -> None:
        self.__definition.validate(value)
        self._validate(value)

    @abstractmethod
    def _validate(self, value: object) -> None: ...

    @override
    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}(name={self.name!r}, "
            f"description={self.description!r}, optional={self.optional!r}, "
            f"definition={self.__definition!r}, default={self.__default!r})"
        )
