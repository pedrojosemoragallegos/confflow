from __future__ import annotations

from typing import Final, final

from typing_extensions import override

from ..definitions.base import Definition, TomlScalar
from ..definitions.text import Text
from ..exceptions import SchemaError
from ..schema import Schema
from ._validation import _validate_collection_bounds
from .base import Entry

ContainerTarget = Definition[TomlScalar] | Schema


@final
class Map(Entry):
    __slots__ = ("__key", "__maximum_entries", "__minimum_entries", "__value")

    @override
    def __init__(  # ty: ignore[invalid-method-override]
        self,
        name: str,
        description: str = "",
        /,
        *,
        required: bool = False,
        value: ContainerTarget,
        key: Definition[str] | None = None,
        minimum_entries: int | None = None,
        maximum_entries: int | None = None,
    ) -> None:
        super().__init__(name, description, required=required)
        if key is not None and (
            not isinstance(key, Definition) or key.value_type is not str
        ):
            raise SchemaError("map key must be a string Definition")
        if not isinstance(value, (Definition, Schema)):
            raise SchemaError("map value must be a Definition or Schema")
        _validate_collection_bounds(minimum_entries, maximum_entries, "map")

        self.__key: Final[Definition[str]] = Text("key") if key is None else key
        self.__value: Final[ContainerTarget] = value
        self.__minimum_entries: Final[int | None] = minimum_entries
        self.__maximum_entries: Final[int | None] = maximum_entries

    @property
    def key(self) -> Definition[str]:
        return self.__key

    @property
    def value(self) -> ContainerTarget:
        return self.__value

    @property
    def minimum_entries(self) -> int | None:
        return self.__minimum_entries

    @property
    def maximum_entries(self) -> int | None:
        return self.__maximum_entries

    @override
    def __repr__(self) -> str:
        return (
            f"Map(name={self.name!r}, description={self.description!r}, "
            f"required={self.required!r}, key={self.__key!r}, value={self.__value!r}, "
            f"minimum_entries={self.__minimum_entries!r}, "
            f"maximum_entries={self.__maximum_entries!r})"
        )
