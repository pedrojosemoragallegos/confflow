from datetime import datetime
from typing import Generic, Iterable, Optional, TypeVar, Union

from ...constraints import Constraint

T = TypeVar("T", bound=Union[str, int, float, bool, datetime, bytes], covariant=True)


class Field(Generic[T]):
    def __init__(
        self,
        name: str,
        description: str,
        *,
        default_value: Optional[T] = None,
        required: bool = False,
        constraints: Optional[Iterable[Constraint[T]]] = None,
    ):
        self._name = name
        self._description = description
        self._required = required
        self._constraints = list(constraints) if constraints else []

        if default_value is not None:
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

    def __repr__(self) -> str:
        return (
            f"Field(name={self._name!r}, "  # QUESTION should we take the private or the property
            f"default={self._default_value!r}, "
            f"required={self._required}, "
            f"constraints={len(self._constraints)})"
        )
