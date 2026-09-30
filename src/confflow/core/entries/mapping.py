from __future__ import annotations

from collections.abc import Mapping as MappingValue
from typing import TYPE_CHECKING, Any, Final, cast, final

from typing_extensions import override

from .._composition_validation import validate_composition
from .._validators import validate_mapping
from ..definitions.base import Definition, Value as DefinitionValue
from ..definitions.exceptions import DefinitionError
from ..definitions.text import Text
from ..exceptions import SchemaError, ValidationError
from ._validators import _validate_collection_bounds
from .base import Entry
from .scalars.base import Scalar

if TYPE_CHECKING:
    from collections.abc import Iterable

    from ..rules.base import Rule


@final
class Mapping(Entry):
    __slots__ = (
        "__entries",
        "__key",
        "__maximum_entries",
        "__minimum_entries",
        "__rules",
        "__value",
    )

    def __init__(
        self,
        name: str,
        description: str | None = None,
        /,
        *,
        optional: bool = False,
        value: Definition[DefinitionValue] | Scalar[Any] | None = None,
        entries: Iterable[Entry] | None = None,
        rules: Iterable[Rule] | None = None,
        key: Definition[str] | Scalar[str] | None = None,
        minimum_entries: int | None = None,
        maximum_entries: int | None = None,
    ) -> None:
        super().__init__(name, description, optional=optional)

        if key is not None:
            if isinstance(key, Scalar):
                key = key.definition
            if not isinstance(key, Definition) or key.VALUE_TYPE is not str:
                raise SchemaError("mapping key must be a string Definition")

        _validate_collection_bounds(minimum_entries, maximum_entries, "mapping")

        if (value is None) == (entries is None):
            raise SchemaError("mapping must define either a value or table entries")
        if value is not None:
            if isinstance(value, Scalar):
                value = value.definition
            if not isinstance(value, Definition):
                raise SchemaError("mapping value must be a Definition")
        if entries is None and rules is not None:
            raise SchemaError("mapping rules require table entries")

        self.__key: Final[Definition[str]] = Text() if key is None else key
        self.__value: Final[Definition[DefinitionValue] | None] = value
        if entries is None:
            self.__entries: Final[tuple[Entry, ...] | None] = None
            self.__rules: Final[tuple[Rule, ...]] = ()
        else:
            self.__entries, self.__rules = validate_composition(
                entries, rules, label="mapping table value"
            )
        self.__minimum_entries: Final[int | None] = minimum_entries
        self.__maximum_entries: Final[int | None] = maximum_entries

    @property
    def key(self) -> Definition[str]:
        return self.__key

    @property
    def value(self) -> Definition[DefinitionValue] | None:
        return self.__value

    @property
    def entries(self) -> tuple[Entry, ...] | None:
        return self.__entries

    @property
    def rules(self) -> tuple[Rule, ...]:
        return self.__rules

    @property
    def minimum_entries(self) -> int | None:
        return self.__minimum_entries

    @property
    def maximum_entries(self) -> int | None:
        return self.__maximum_entries

    def validate(self, value: object) -> None:
        if not isinstance(value, MappingValue):
            raise ValidationError("expected a mapping", ())

        if self.__minimum_entries is not None and len(value) < self.__minimum_entries:
            raise ValidationError("mapping has fewer entries than the minimum", ())
        if self.__maximum_entries is not None and len(value) > self.__maximum_entries:
            raise ValidationError("mapping exceeds the maximum number of entries", ())

        mapping = cast("MappingValue[object, object]", value)
        for key, mapped_value in mapping.items():
            if type(key) is not str:
                raise ValidationError("mapping keys must be strings", ())
            key_path = (key,)
            try:
                self.__key.validate(key)
                if self.__value is not None:
                    self.__value.validate(mapped_value)
                else:
                    validate_mapping(
                        self.__entries or (), self.__rules, mapped_value, key_path
                    )
            except DefinitionError as error:
                raise ValidationError(str(error), key_path) from None
            except ValidationError as error:
                if error.path == ():
                    raise type(error)(str(error), key_path) from None
                raise

    @override
    def __repr__(self) -> str:
        return (
            f"Mapping(name={self.name!r}, description={self.description!r}, "
            f"optional={self.optional!r}, key={self.__key!r}, value={self.__value!r}, "
            f"entries={self.__entries!r}, rules={self.__rules!r}, "
            f"minimum_entries={self.__minimum_entries!r}, "
            f"maximum_entries={self.__maximum_entries!r})"
        )
