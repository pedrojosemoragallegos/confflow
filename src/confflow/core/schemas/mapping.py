from __future__ import annotations

from collections.abc import Mapping as MappingABC
from typing import Final

from typing_extensions import override

from confflow.core.definitions import String as StringDefinition
from confflow.core.schemas.base import Schema
from confflow.core.schemas.exceptions import SchemaError


class Key:
    __slots__ = ("__definition",)

    def __init__(
        self,
        *,
        minimum: int | None = None,
        maximum: int | None = None,
        length: int | None = None,
        pattern: str | None = None,
    ) -> None:
        self.__definition: Final[StringDefinition] = StringDefinition(
            minimum=minimum, maximum=maximum, length=length, pattern=pattern
        )

    def validate(self, value: object, /) -> None:
        self.__definition.validate(value)

    @override
    def __repr__(self) -> str:
        return f"{type(self).__name__}(definition={self.__definition!r})"


class Mapping(Schema):
    __slots__ = ("__key", "__value")

    def __init__(
        self,
        name: str,
        description: str | None = None,
        /,
        *,
        optional: bool = False,
        key: Key | None = None,
        value: Schema,
    ) -> None:
        super().__init__(name, description, optional=optional)

        self.__key: Final[Key] = key or Key()
        self.__value: Final[Schema] = value

    @property
    def key(self) -> Key:
        return self.__key

    @property
    def value(self) -> Schema:
        return self.__value

    @override
    def validate(self, value: object, /) -> None:
        super().validate(value)

        if not isinstance(value, MappingABC):
            raise SchemaError("mapping value must be a mapping")

        for key, item in value.items():
            self.__key.validate(key)
            self.__value.validate(item)

    @override
    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}(name={self.name!r}, "
            f"description={self.description!r}, "
            f"optional={self.optional!r}, "
            f"key={self.__key!r}, "
            f"value={self.__value!r})"
        )
