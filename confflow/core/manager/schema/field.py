from typing import Generic, Optional, TypeVar

from confflow.core.field.constraint.constraint import Constraint
from confflow.types import Value, View
from confflow.utils import freeze

T = TypeVar("T", bound=Value)


class Field(Generic[T]):
    def __init__(
        self,
        name: str,
        description: str,
        default_value: Optional[T],
        required: bool,
        *constraint: Constraint[T],
    ):
        self._name = name
        self._description = description
        self._default_value = default_value
        self._required = required
        self._constraints = list(constraint)

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    @property
    def default_value(self) -> View:
        return freeze(self._name)

    @property
    def required(self) -> bool:
        return self._required

    @property
    def constraints(self):  # TODO correct return type
        return tuple(self._constraints)

    def __repr__(self) -> str:
        constraints_repr = ", ".join(repr(c) for c in self._constraints)
        return (
            f"{self.__class__.__name__}("
            f"name={self._name!r}, "
            f"default_value={self._default_value!r}, "
            f"required={self._required}, "
            f"constraints=[{constraints_repr}]"
            f")"
        )
