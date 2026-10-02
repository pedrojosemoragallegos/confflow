from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, ClassVar, Generic, TypeVar

from confflow.core.errors import ValidationError, constraint_rule
from confflow.core.types import Value

if TYPE_CHECKING:
    from confflow.core.definitions.constraints import Constraint

ValueT = TypeVar(name="ValueT", bound=Value)


class Definition(ABC, Generic[ValueT]):
    __slots__ = ("__constraints",)

    VALUE_TYPE: ClassVar[type[Value]]

    def __init__(self, *constraints: Constraint[ValueT]) -> None:
        self.__constraints: tuple[Constraint[ValueT], ...] = constraints

    @property
    def constraints(self) -> tuple[Constraint[ValueT], ...]:
        return self.__constraints

    def validate(self, value: ValueT, /) -> None:
        for constraint in self.__constraints:
            try:
                constraint(value)
            except ValidationError:
                raise
            except (TypeError, ValueError, RuntimeError) as error:
                raise ValidationError(
                    str(error),
                    value=value,
                    constraint=constraint.NAME,
                    expected=constraint_rule(constraint),
                ) from error

    @abstractmethod
    def __repr__(self) -> str: ...
