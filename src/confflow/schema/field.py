from __future__ import annotations

import typing
from datetime import datetime

from confflow.constraints import (
    AllItemsMatch,
    Constraint,
    EnumValues,
    GreaterThan,
    GreaterThanOrEqual,
    LessThan,
    LessThanOrEqual,
    MaxItems,
    MaxLength,
    MinItems,
    MinLength,
    Regex,
    UniqueItems,
)

if typing.TYPE_CHECKING:
    from collections.abc import Sequence

T = typing.TypeVar(
    "T",
    str,
    int,
    float,
    bool,
    datetime,
    bytes,
    list[str],
    list[int],
    list[float],
    list[bool],
    list[datetime],
    list[bytes],
)


class Field(typing.Generic[T]):
    def __init__(
        self,
        name: str,
        *,
        description: str,
        default_value: T | None = None,
        constraints: Sequence[Constraint[T]] | None = None,
    ) -> None:
        self._name: str = name
        self._description: str = description

        if constraints and len(constraints) != len({type(c) for c in constraints}):
            raise ValueError("Cannot have multiple constraints of the same type")  # noqa: EM101, TRY003

        self._constraints: frozenset[Constraint[T]] = (
            frozenset(constraints) if constraints else frozenset()
        )

        self._default_value: T | None = (
            self._validate(default_value)
            if default_value is not None
            else default_value
        )

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    @property
    def default_value(self) -> T | None:
        return self._default_value

    @property
    def constraints(self) -> frozenset[Constraint[T]]:
        return self._constraints

    def _validate(self, value: T) -> T:
        for constraint in self._constraints:
            constraint(value)

        return value

    def __repr__(self) -> str:
        return (
            f"Field(name={self.name!r}, "
            f"default={self.default_value!r}, "
            f"constraints={len(self.constraints)})"
        )


class StringField(Field[str]):
    def __init__(  # noqa: PLR0913
        self,
        name: str,
        *,
        description: str,
        default_value: str | None = None,
        min_length: int | None = None,
        max_length: int | None = None,
        regex: str | None = None,
        enum: list[str] | None = None,
    ) -> None:
        constraints: list[Constraint[str]] = []
        if min_length:
            constraints.append(MinLength(min_length))
        if max_length:
            constraints.append(MaxLength(max_length))
        if regex:
            constraints.append(Regex(regex))
        if enum:
            constraints.append(EnumValues(enum))

        super().__init__(
            name=name,
            description=description,
            default_value=default_value,
            constraints=constraints,
        )


class StringListField(Field[list[str]]):
    def __init__(  # noqa: PLR0913
        self,
        name: str,
        *,
        description: str,
        default_value: list[str] | None = None,
        min_items: int | None = None,
        max_items: int | None = None,
        unique_items: bool | None = None,
        min_length: int | None = None,
        max_length: int | None = None,
        regex: str | None = None,
        enum: list[str] | None = None,
    ) -> None:
        constraints: list[Constraint[list[str]]] = []
        if min_items:
            constraints.append(MinItems(min_items))
        if max_items:
            constraints.append(MaxItems(max_items))
        if unique_items:
            constraints.append(UniqueItems())

        item_constraints: list[Constraint[str]] = []
        if min_length:
            item_constraints.append(MinLength(min_length))
        if max_length:
            item_constraints.append(MaxLength(max_length))
        if regex:
            item_constraints.append(Regex(regex))
        if enum:
            item_constraints.append(EnumValues(enum))

        if item_constraints:
            constraints.append(AllItemsMatch[str](*item_constraints))

        super().__init__(
            name=name,
            description=description,
            default_value=default_value,
            constraints=constraints,
        )


class IntegerField(Field[int]):
    def __init__(  # noqa: PLR0913
        self,
        name: str,
        *,
        description: str,
        default_value: int | None = None,
        gt: int | None = None,
        ge: int | None = None,
        lt: int | None = None,
        le: int | None = None,
    ) -> None:
        constraints: list[Constraint[int]] = []

        if gt:
            constraints.append(GreaterThan(gt))
        if ge:
            constraints.append(GreaterThanOrEqual(ge))
        if lt:
            constraints.append(LessThan(lt))
        if le:
            constraints.append(LessThanOrEqual(le))

        super().__init__(
            name=name,
            description=description,
            default_value=default_value,
            constraints=constraints,
        )


class IntegerListField(Field[list[int]]):
    def __init__(  # noqa: PLR0913
        self,
        name: str,
        *,
        description: str,
        default_value: list[int] | None = None,
        min_items: int | None = None,
        max_items: int | None = None,
        unique_items: bool | None = None,
        gt: int | None = None,
        ge: int | None = None,
        lt: int | None = None,
        le: int | None = None,
    ) -> None:
        constraints: list[Constraint[list[int]]] = []

        if min_items:
            constraints.append(MinItems(min_items))
        if max_items:
            constraints.append(MaxItems(max_items))
        if unique_items:
            constraints.append(UniqueItems())

        item_constraints: list[Constraint[int]] = []

        if gt:
            item_constraints.append(GreaterThan(gt))
        if ge:
            item_constraints.append(GreaterThanOrEqual(ge))
        if lt:
            item_constraints.append(LessThan(lt))
        if le:
            item_constraints.append(LessThanOrEqual(le))

        if item_constraints:
            constraints.append(
                AllItemsMatch[int](*item_constraints),
            )

        super().__init__(
            name=name,
            description=description,
            default_value=default_value,
            constraints=constraints,
        )


class FloatField(Field[float]):
    def __init__(  # noqa: PLR0913
        self,
        name: str,
        *,
        description: str,
        default_value: float | None = None,
        gt: float | None = None,
        ge: float | None = None,
        lt: float | None = None,
        le: float | None = None,
    ) -> None:
        constraints: list[Constraint[float]] = []

        if gt:
            constraints.append(GreaterThan(gt))
        if ge:
            constraints.append(GreaterThanOrEqual(ge))
        if lt:
            constraints.append(LessThan(lt))
        if le:
            constraints.append(LessThanOrEqual(le))

        super().__init__(
            name=name,
            description=description,
            default_value=default_value,
            constraints=constraints,
        )


class FloatListField(Field[list[float]]):
    def __init__(  # noqa: PLR0913
        self,
        name: str,
        *,
        description: str,
        default_value: list[float] | None = None,
        min_items: int | None = None,
        max_items: int | None = None,
        unique_items: bool | None = None,
        gt: float | None = None,
        ge: float | None = None,
        lt: float | None = None,
        le: float | None = None,
    ) -> None:
        constraints: list[Constraint[list[float]]] = []

        if min_items:
            constraints.append(MinItems(min_items))
        if max_items:
            constraints.append(MaxItems(max_items))
        if unique_items:
            constraints.append(UniqueItems())

        item_constraints: list[Constraint[float]] = []

        if gt:
            item_constraints.append(GreaterThan(gt))
        if ge:
            item_constraints.append(GreaterThanOrEqual(ge))
        if lt:
            item_constraints.append(LessThan(lt))
        if le:
            item_constraints.append(LessThanOrEqual(le))

        if item_constraints:
            constraints.append(AllItemsMatch[float](*item_constraints))

        super().__init__(
            name=name,
            description=description,
            default_value=default_value,
            constraints=constraints,
        )


class DateField(Field[datetime]):
    def __init__(
        self,
        name: str,
        *,
        description: str,
        default_value: datetime | None = None,
    ) -> None:
        super().__init__(
            name=name,
            description=description,
            default_value=default_value,
            constraints=[],
        )


class DateListField(Field[list[datetime]]):
    def __init__(  # noqa: PLR0913
        self,
        name: str,
        *,
        description: str,
        default_value: list[datetime] | None = None,
        min_items: int | None = None,
        max_items: int | None = None,
        unique_items: bool | None = None,
    ) -> None:
        constraints: list[Constraint[list[datetime]]] = []

        if min_items:
            constraints.append(MinItems(min_items))
        if max_items:
            constraints.append(MaxItems(max_items))
        if unique_items:
            constraints.append(UniqueItems())

        super().__init__(
            name=name,
            description=description,
            default_value=default_value,
            constraints=constraints,
        )


class BytesField(Field[bytes]):
    def __init__(
        self,
        name: str,
        *,
        description: str,
        default_value: bytes | None = None,
    ) -> None:
        super().__init__(
            name=name,
            description=description,
            default_value=default_value,
            constraints=[],
        )


class BooleanListField(Field[list[bool]]):
    def __init__(  # noqa: PLR0913
        self,
        name: str,
        *,
        description: str,
        default_value: list[bool] | None = None,
        min_items: int | None = None,
        max_items: int | None = None,
        unique_items: bool | None = None,
    ) -> None:
        constraints: list[Constraint[list[bool]]] = []

        if min_items:
            constraints.append(MinItems(min_items))
        if max_items:
            constraints.append(MaxItems(max_items))
        if unique_items:
            constraints.append(UniqueItems())

        super().__init__(
            name=name,
            description=description,
            default_value=default_value,
            constraints=constraints,
        )


class BooleanField(Field[bool]):
    def __init__(
        self,
        name: str,
        *,
        description: str,
        default_value: bool | None = None,
    ) -> None:
        super().__init__(
            name=name,
            description=description,
            default_value=default_value,
            constraints=[],
        )


class BytesListField(Field[list[bytes]]):
    def __init__(  # noqa: PLR0913
        self,
        name: str,
        *,
        description: str,
        default_value: list[bytes] | None = None,
        min_items: int | None = None,
        max_items: int | None = None,
        unique_items: bool | None = None,
    ) -> None:
        constraints: list[Constraint[list[bytes]]] = []

        if min_items:
            constraints.append(MinItems(min_items))
        if max_items:
            constraints.append(MaxItems(max_items))
        if unique_items:
            constraints.append(UniqueItems())

        super().__init__(
            name=name,
            description=description,
            default_value=default_value,
            constraints=constraints,
        )
