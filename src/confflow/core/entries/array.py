from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING, Any, Final, cast, final

from typing_extensions import override

from .._composition_validation import validate_composition
from .._validators import validate_mapping
from ..definitions.base import Definition, Value as DefinitionValue
from ..definitions.exceptions import DefinitionError
from ..exceptions import SchemaError, ValidationError
from ._validators import _validate_collection_bounds
from .base import Entry
from .scalars.base import Scalar

if TYPE_CHECKING:
    from collections.abc import Iterable

    from ..rules.base import Rule


@final
class Array(Entry):
    __slots__ = (
        "__element",
        "__entries",
        "__maximum_length",
        "__minimum_length",
        "__rules",
        "__unique",
    )

    def __init__(
        self,
        name: str,
        description: str | None,
        /,
        *,
        element: Definition[DefinitionValue] | Scalar[Any] | None = None,
        entries: Iterable[Entry] | None = None,
        rules: Iterable[Rule] | None = None,
        optional: bool = False,
        minimum_length: int | None = None,
        maximum_length: int | None = None,
        unique: bool = False,
    ) -> None:
        super().__init__(name, description, optional=optional)

        _validate_collection_bounds(minimum_length, maximum_length, "array")

        if (element is None) == (entries is None):
            raise SchemaError("array must define either an element or table entries")
        if element is not None:
            if isinstance(element, Scalar):
                element = element.definition
            if not isinstance(element, Definition):
                raise SchemaError("array element must be a Definition or Scalar entry")
        if entries is not None and unique:
            raise SchemaError("unique arrays require a Definition element")
        if entries is None and rules is not None:
            raise SchemaError("array rules require table entries")

        self.__element: Final[Definition[DefinitionValue] | None] = element
        if entries is None:
            self.__entries: Final[tuple[Entry, ...] | None] = None
            self.__rules: Final[tuple[Rule, ...]] = ()
        else:
            self.__entries, self.__rules = validate_composition(
                entries, rules, label="array table element"
            )
        self.__minimum_length: Final[int | None] = minimum_length
        self.__maximum_length: Final[int | None] = maximum_length
        self.__unique: Final[bool] = unique

    @property
    def element(self) -> Definition[DefinitionValue] | None:
        return self.__element

    @property
    def entries(self) -> tuple[Entry, ...] | None:
        return self.__entries

    @property
    def rules(self) -> tuple[Rule, ...]:
        return self.__rules

    @property
    def minimum_length(self) -> int | None:
        return self.__minimum_length

    @property
    def maximum_length(self) -> int | None:
        return self.__maximum_length

    @property
    def unique(self) -> bool:
        return self.__unique

    def validate(self, value: object) -> None:
        if not isinstance(value, Sequence) or isinstance(
            value, (str, bytes, bytearray)
        ):
            raise ValidationError("expected an array", ())
        array_value = cast("Sequence[object]", value)
        if (
            self.__minimum_length is not None
            and len(array_value) < self.__minimum_length
        ):
            raise ValidationError("array is shorter than the minimum length", ())
        if (
            self.__maximum_length is not None
            and len(array_value) > self.__maximum_length
        ):
            raise ValidationError("array exceeds the maximum length", ())
        if self.__unique:
            for index, element in enumerate(array_value):
                if any(element == previous for previous in array_value[:index]):
                    raise ValidationError("array elements must be unique", (index,))

        for index, item in enumerate(array_value):
            item_path = (index,)
            if self.__element is not None:
                _validate_definition(self.__element, item, item_path)
            else:
                validate_mapping(self.__entries or (), self.__rules, item, item_path)

    @override
    def __repr__(self) -> str:
        return (
            f"Array(name={self.name!r}, description={self.description!r}, "
            f"optional={self.optional!r}, "
            f"element={self.__element!r}, entries={self.__entries!r}, "
            f"rules={self.__rules!r}, minimum_length={self.__minimum_length!r}, "
            f"maximum_length={self.__maximum_length!r}, unique={self.__unique!r})"
        )


def _validate_definition(
    definition: Definition[DefinitionValue],
    value: object,
    path: tuple[str | int, ...],
) -> None:
    try:
        definition.validate(value)
    except DefinitionError as error:
        raise ValidationError(str(error), path) from None
    except ValidationError as error:
        if error.path == ():
            raise type(error)(str(error), path) from None
        raise
