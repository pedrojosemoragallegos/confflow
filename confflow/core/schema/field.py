from typing import TYPE_CHECKING, Generic, Optional, TypeVar

from confflow.types import Value

if TYPE_CHECKING:
    from ..config import Constraint

T = TypeVar("T", bound=Value, covariant=True)


class Field(Generic[T]):
    def __init__(
        self,
        name: str,
        description: str,
        default_value: Optional[T] = None,
        required: bool = False,
        constraints: Optional[list[Constraint[T]]] = None,
    ):
        self._name = name
        self._description = description
        self._required = required
        self._constraints = constraints if constraints else []

        if default_value:
            for constraint in self._constraints:
                constraint(default_value)

        self._default_value = default_value

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    @property
    def default_value(self) -> Optional[T]:
        return self._default_value

    @property
    def required(self) -> bool:
        return self._required

    @property
    def constraints(self) -> list[Constraint[T]]:
        return self._constraints
