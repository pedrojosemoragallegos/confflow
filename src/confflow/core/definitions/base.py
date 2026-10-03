from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Final, Generic, TypeVar, final

from confflow.core.errors import ValidationError, constraint_name, constraint_rule
from confflow.core.types import Value

if TYPE_CHECKING:
    from confflow.core.definitions.constraints import Constraint

ValueT = TypeVar(name="ValueT", bound=Value)


class Definition(ABC, Generic[ValueT]):
    __slots__ = ("__constraints",)

    def __init__(self, *constraints: Constraint[ValueT]) -> None:
        self.__constraints: Final[tuple[Constraint[ValueT], ...]] = constraints

    @property
    @final
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
                    str(object=error),
                    value=value,
                    constraint=constraint_name(constraint),
                    expected=constraint_rule(constraint),
                ) from error

    @abstractmethod
    def __repr__(self) -> str: ...
