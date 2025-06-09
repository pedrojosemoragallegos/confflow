from typing import Generic, Optional, TypeVar

from confflow.types import Value

from ..config import FieldConstraint

T = TypeVar("T", bound=Value, covariant=True)


class Field(Generic[T]):
    def __init__(
        self,
        name: str,
        description: str,
        default_value: Optional[T] = None,
        required: bool = False,
        *constraint: FieldConstraint[T],
    ):
        self._name = name
        self._description = description
        self._default_value = default_value
        self._required = required
        self._constraints: list[FieldConstraint[T]] = list(constraint)

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
    def constraints(self) -> list[FieldConstraint[T]]:
        return self._constraints
