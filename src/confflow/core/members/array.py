from __future__ import annotations

from typing import Final, final

from typing_extensions import override

from ..definitions.base import Definition, TomlScalar
from ..exceptions import SchemaError
from ..schema import Schema
from ._validation import _validate_collection_bounds
from .base import Entry

ContainerTarget = Definition[TomlScalar] | Schema


@final
class Array(Entry):
    __slots__ = ("__element", "__maximum_length", "__minimum_length", "__unique")

    @override
    def __init__(  # ty: ignore[invalid-method-override]
        self,
        name: str,
        description: str,
        element: ContainerTarget,
        /,
        *,
        required: bool = False,
        minimum_length: int | None = None,
        maximum_length: int | None = None,
        unique: bool = False,
    ) -> None:
        super().__init__(name, description, required=required)
        if not isinstance(element, (Definition, Schema)):
            raise SchemaError("array element must be a Definition or Schema")
        _validate_collection_bounds(minimum_length, maximum_length, "array")
        if type(unique) is not bool:
            raise SchemaError("array uniqueness flag must be a boolean")
        if unique and isinstance(element, Schema):
            raise SchemaError("unique arrays require a Definition element")

        self.__element: Final[ContainerTarget] = element
        self.__minimum_length: Final[int | None] = minimum_length
        self.__maximum_length: Final[int | None] = maximum_length
        self.__unique: Final[bool] = unique

    @property
    def element(self) -> ContainerTarget:
        return self.__element

    @property
    def minimum_length(self) -> int | None:
        return self.__minimum_length

    @property
    def maximum_length(self) -> int | None:
        return self.__maximum_length

    @property
    def unique(self) -> bool:
        return self.__unique

    @override
    def __repr__(self) -> str:
        return (
            f"Array(name={self.name!r}, description={self.description!r}, "
            f"required={self.required!r}, "
            f"element={self.__element!r}, minimum_length={self.__minimum_length!r}, "
            f"maximum_length={self.__maximum_length!r}, unique={self.__unique!r})"
        )
