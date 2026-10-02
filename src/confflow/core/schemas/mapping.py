from __future__ import annotations

from collections.abc import Mapping as MappingABC
from typing import TYPE_CHECKING, Final, Generic, TypeVar

from typing_extensions import override

from confflow.core.definitions import String as StringDefinition
from confflow.core.errors import ValidationError
from confflow.core.schemas.base import Schema

if TYPE_CHECKING:
    from confflow.core.definitions.constraints import Constraint

ValueT = TypeVar(name="ValueT")


class Key:
    __slots__ = ("__definition",)

    def __init__(
        self,
        *constraints: Constraint[str],
        minimum: int | None = None,
        maximum: int | None = None,
        pattern: str | None = None,
    ) -> None:
        self.__definition: Final[StringDefinition] = StringDefinition(
            *constraints, minimum=minimum, maximum=maximum, pattern=pattern
        )

    @property
    def definition(self) -> StringDefinition:
        return self.__definition

    def validate(self, value: str, /) -> None:
        self.__definition.validate(value)

    @override
    def __repr__(self) -> str:
        return f"{type(self).__name__}(definition={self.__definition!r})"


class Mapping(
    Schema[MappingABC[str, ValueT]],
    Generic[ValueT],
):
    __slots__ = ("__key", "__value")

    def __init__(
        self,
        name: str,
        description: str | None,
        /,
        *,
        optional: bool = False,
        key: Key | None = None,
        value: Schema[ValueT],
    ) -> None:
        super().__init__(
            name,
            description,
            optional=optional,
        )

        self.__key: Final[Key] = key or Key()
        self.__value: Final[Schema[ValueT]] = value

    @property
    def key(self) -> Key:
        return self.__key

    @property
    def value(self) -> Schema[ValueT]:
        return self.__value

    @override
    def validate(self, value: MappingABC[str, ValueT], /) -> None:
        for key, item in value.items():
            try:
                self.__key.validate(key)
            except ValidationError as error:
                error.prepend_path("key")
                raise
            except (TypeError, ValueError, RuntimeError) as error:
                raise ValidationError(
                    str(object=error), path=("key",), value=key, expected="mapping key"
                ) from error

            try:
                self.__value.validate(item)
            except ValidationError as error:
                error.prepend_path(f"[{key!r}]")
                raise
            except (TypeError, ValueError, RuntimeError) as error:
                raise ValidationError(
                    str(object=error),
                    path=(f"[{key!r}]",),
                    value=item,
                    expected=type(self.__value).__name__,
                ) from error

    @override
    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}("
            f"name={self.name!r}, "
            f"description={self.description!r}, "
            f"optional={self.optional!r}, "
            f"key={self.__key!r}, "
            f"value={self.__value!r})"
        )
