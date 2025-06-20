from datetime import datetime
from typing import Optional, TypeAlias, Union

from confflow.core.config.field.constraint import (
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

from ...types import ListValue
from .field import Field, FieldConstraint

FieldValue: TypeAlias = Union[
    Field[str],
    Field[int],
    Field[float],
    Field[bool],
    Field[datetime],
    Field[bytes],
    Field[ListValue],
]

Entry: TypeAlias = Union[
    FieldValue,
    "Schema",
]


class Schema:
    def __init__(self, name: str, description: str):
        self._name = name
        self._description = description
        self._entries: dict[  # TODO dict or ordered dict?
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
    def fields(self):  # TODO correct return type
        return self._entries.values()

    def SubSchema(self, name: str, schema: "Schema"):
        self._entries[name] = schema

        return self

    def String(
        self,
        name: str,
        description: str,
        default_value: Optional[str] = None,
        min_length: Optional[str] = None,
        max_length: Optional[str] = None,
        regex: Optional[str] = None,
        # validate: Optional[Callable[[str], str]] = None,
    ):
        constraints: list[FieldConstraint[str]] = []

        if min_length:
            constraints.append(MinLength(min_length))
        if max_length:
            constraints.append(MaxLength(max_length))
        if regex:
            constraints.append(Regex(regex))

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
        # validate: Optional[Callable[[int], int]] = None,
    ):
        constraints: list[FieldConstraint[int]] = []

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
        # validate: Optional[Callable[[float], float]] = None,
    ):
        constraints: list[FieldConstraint[float]] = []

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
        # validate: Optional[Callable[[datetime], datetime]] = None,
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
        # validate: Optional[Callable[[bytes], bytes]] = None,
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
        default_value: Optional[ListValue] = None,
        min_items: Optional[int] = None,
        max_items: Optional[int] = None,
        unique_itmes: Optional[bool] = None,
        # validate: Optional[Callable[[list], list]] = None,
    ):
        constraints: list[FieldConstraint[list]] = []

        if min_items:
            constraints.append(MinItems(min_items))
        if max_items:
            constraints.append(MaxItems(max_items))
        if unique_itmes:
            constraints.append(UniqueItems())

        self._entries[name] = Field[ListValue](
            name=name,
            description=description,
            default_value=default_value,
            required=True if default_value else False,
            constraints=constraints,
        )
        return self

    def keys(self):  # TODO  return type
        return self._entries.keys()

    def values(self):  # TODO  return type
        return self._entries.values()

    def items(self):  # TODO  return type
        return self._entries.items()

    def __getitem__(self, key: str):  # TODO  return type
        return self._entries[key]

    def __contains__(self, key: str):  # TODO  return type
        return key in self._entries

    # Only for iPython # TODO maybe remove here  as mixin or so
    def _ipython_key_completions_(self) -> list[str]:
        return list(self._entries.keys())
