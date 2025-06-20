from collections.abc import ItemsView, KeysView, ValuesView
from datetime import datetime
from typing import Optional, TypeAlias, Union

from confflow.core.config.field.constraint import (
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

from .field import Constraint, Field

ListValue: TypeAlias = Union[str, int, float, bool, datetime, bytes]
FieldValue: TypeAlias = Union[
    Field[str],
    Field[int],
    Field[float],
    Field[bool],
    Field[datetime],
    Field[bytes],
    Field[list[ListValue]],
]

Entry: TypeAlias = Union[
    FieldValue,
    "Schema",
]


class Schema:
    def __init__(self, name: str, description: str):
        self._name = name
        self._description = description
        self._entries: dict[
            str,
            Entry,
        ] = dict()

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    @property
    def fields(self) -> ValuesView[Entry]:
        return self._entries.values()

    def SubSchema(self, name: str, schema: "Schema"):
        self._entries[name] = schema

        return self

    def String(
        self,
        name: str,
        description: str,
        default_value: Optional[str] = None,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        regex: Optional[str] = None,
        enum: Optional[list[str]] = None,
    ):
        constraints: list[Constraint[str]] = []

        if min_length:
            constraints.append(MinLength(min_length))
        if max_length:
            constraints.append(MaxLength(max_length))
        if regex:
            constraints.append(Regex(regex))
        if enum:
            constraints.append(EnumValues(enum))

        self._entries[name] = Field[str](
            name=name,
            description=description,
            default_value=default_value,
            required=True if default_value else False,
            constraints=constraints,
        )

        return self

    def Integer(
        self,
        name: str,
        description: str,
        default_value: Optional[int] = None,
        gt: Optional[int] = None,
        ge: Optional[int] = None,
        lt: Optional[int] = None,
        le: Optional[int] = None,
    ):
        constraints: list[Constraint[int]] = []

        if gt:
            constraints.append(GreaterThan(gt))
        if ge:
            constraints.append(GreaterThanOrEqual(ge))
        if lt:
            constraints.append(LessThan(lt))
        if le:
            constraints.append(LessThanOrEqual(le))

        self._entries[name] = Field[int](
            name=name,
            description=description,
            default_value=default_value,
            required=True if default_value is not None else False,
            constraints=constraints,
        )

        return self

    def Float(
        self,
        name: str,
        description: str,
        default_value: Optional[float] = None,
        gt: Optional[float] = None,
        ge: Optional[float] = None,
        lt: Optional[float] = None,
        le: Optional[float] = None,
    ):
        constraints: list[Constraint[float]] = []

        if gt:
            constraints.append(GreaterThan(gt))
        if ge:
            constraints.append(GreaterThanOrEqual(ge))
        if lt:
            constraints.append(LessThan(lt))
        if le:
            constraints.append(LessThanOrEqual(le))

        self._entries[name] = Field[float](
            name=name,
            description=description,
            default_value=default_value,
            required=True if default_value is not None else False,
        )

        return self

    def Boolean(
        self,
        name: str,
        description: str,
        default_value: Optional[bool] = None,
    ):
        self._entries[name] = Field[bool](
            name=name,
            description=description,
            default_value=default_value,
            required=True if default_value is not None else False,
        )

        return self

    def Date(
        self,
        name: str,
        description: str,
        default_value: Optional[datetime] = None,
    ):
        self._entries[name] = Field[datetime](
            name=name,
            description=description,
            default_value=default_value,
            required=True if default_value is not None else False,
        )

        return self

    def Bytes(
        self,
        name: str,
        description: str,
        default_value: Optional[bytes] = None,
    ):
        self._entries[name] = Field[bytes](
            name=name,
            description=description,
            default_value=default_value,
            required=True if default_value is not None else False,
        )

        return self

    def List(
        self,
        name: str,
        description: str,
        default_value: Optional[list[ListValue]] = None,
        min_items: Optional[int] = None,
        max_items: Optional[int] = None,
        unique_itmes: Optional[bool] = None,
    ):
        constraints: list[Constraint[list[ListValue]]] = []

        if min_items:
            constraints.append(MinItems(min_items))
        if max_items:
            constraints.append(MaxItems(max_items))
        if unique_itmes:
            constraints.append(UniqueItems())

        self._entries[name] = Field[list[ListValue]](
            name=name,
            description=description,
            default_value=default_value,
            required=True if default_value else False,
            constraints=constraints,
        )
        return self

    def keys(self) -> KeysView[str]:
        return self._entries.keys()

    def values(self) -> ValuesView[Entry]:
        return self._entries.values()

    def items(self) -> ItemsView[str, Entry]:
        return self._entries.items()

    def __getitem__(self, key: str) -> Entry:
        return self._entries[key]

    def __contains__(self, key: str) -> bool:
        return key in self._entries

    # Only for iPython # TODO maybe remove here  as mixin or so
    def _ipython_key_completions_(self) -> list[str]:
        return list(self._entries.keys())
