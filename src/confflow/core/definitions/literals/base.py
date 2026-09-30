from __future__ import annotations

from math import isnan
from typing import ClassVar, Final, Generic, TypeVar, cast

from typing_extensions import override

from ...exceptions import SchemaError
from ..base import Definition, Value as ScalarValue
from ..exceptions import DefinitionError
from ._validators import validate_scalar_type_values

ValueT = TypeVar(name="ValueT", bound=ScalarValue)

_MINIMUM_VALUES = 2


class Literal(Definition[ValueT], Generic[ValueT]):
    __slots__ = ("__value_type", "__values")

    VALUE_TYPE: ClassVar[type[ScalarValue]]

    def __init__(self, *values: ValueT) -> None:
        if type(self) is Literal:
            raise TypeError("Literal is an abstract base class")

        if len(values) < _MINIMUM_VALUES:
            raise SchemaError("literal must contain at least two values")

        if any(type(value) is not self.VALUE_TYPE for value in values):
            raise SchemaError("literal values must all have the same TOML scalar type")

        self._validate_literal_values(
            values=cast(typ="tuple[ScalarValue, ...]", val=values),
        )

        if len(set(values)) != len(values):
            raise SchemaError("literal values cannot contain duplicates")

        self.__values: Final[tuple[ValueT, ...]] = values
        self.__value_type: Final[type[ScalarValue]] = self.VALUE_TYPE

    def _validate_literal_values(self, values: tuple[ScalarValue, ...]) -> None:
        validate_scalar_type_values(value_type=self.VALUE_TYPE, value_tuple=values)

    @override
    def validate(self, value: object) -> None:
        if type(value) is not self.__value_type:
            raise DefinitionError("value does not use the literal's TOML scalar type")

        if self.__value_type is float and isnan(cast(typ="float", val=value)):
            raise DefinitionError("NaN is not allowed")

        if value not in self.__values:
            raise DefinitionError("value is not one of the literal values")

    @override
    def __repr__(self) -> str:
        return f"{type(self).__name__}(values={self.__values!r})"
