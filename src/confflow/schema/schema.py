from __future__ import annotations

import typing
from collections import OrderedDict

from confflow.mixins import IPythonMixin

if typing.TYPE_CHECKING:
    from datetime import datetime

    from .field import Field


class Schema(IPythonMixin):
    def __init__(self, name: str, *, description: str) -> None:
        self._name: str = name
        self._description: str = description
        self._fields: dict[
            str,
            Field[str]
            | Field[int]
            | Field[float]
            | Field[bool]
            | Field[datetime]
            | Field[bytes]
            | Field[list[str]]
            | Field[list[int]]
            | Field[list[float]]
            | Field[list[bool]]
            | Field[list[datetime]]
            | Field[list[bytes]]
            | Schema,
        ] = OrderedDict()

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    @property
    def fields(
        self,
    ) -> typing.ValuesView[
        Field[str]
        | Field[int]
        | Field[float]
        | Field[bool]
        | Field[datetime]
        | Field[bytes]
        | Field[list[str]]
        | Field[list[int]]
        | Field[list[float]]
        | Field[list[bool]]
        | Field[list[datetime]]
        | Field[list[bytes]]
        | Schema,
    ]:
        return self._fields.values()

    @typing.overload
    def add(
        self,
        item: Field[str]
        | Field[int]
        | Field[float]
        | Field[bool]
        | Field[datetime]
        | Field[bytes]
        | Field[list[str]]
        | Field[list[int]]
        | Field[list[float]]
        | Field[list[bool]]
        | Field[list[datetime]]
        | Field[list[bytes]],
    ) -> Schema: ...

    @typing.overload
    def add(self, item: Schema) -> Schema: ...

    def add(
        self,
        item: Field[str]
        | Field[int]
        | Field[float]
        | Field[bool]
        | Field[datetime]
        | Field[bytes]
        | Field[list[str]]
        | Field[list[int]]
        | Field[list[float]]
        | Field[list[bool]]
        | Field[list[datetime]]
        | Field[list[bytes]]
        | Schema,
    ) -> Schema:
        if isinstance(item, Schema):
            if item == self:
                raise ValueError("Schema cannot be added to itself")  # noqa: EM101, TRY003
            self._fields.update(item._fields)
        else:  # Field
            self._fields[item.name] = item
        return self

    def keys(
        self,
    ) -> typing.KeysView[str]:
        return self._fields.keys()

    def values(
        self,
    ) -> typing.ValuesView[
        Field[str]
        | Field[int]
        | Field[float]
        | Field[bool]
        | Field[datetime]
        | Field[bytes]
        | Field[list[str]]
        | Field[list[int]]
        | Field[list[float]]
        | Field[list[bool]]
        | Field[list[datetime]]
        | Field[list[bytes]]
        | Schema,
    ]:
        return self._fields.values()

    def items(
        self,
    ) -> typing.ItemsView[
        str,
        Field[str]
        | Field[int]
        | Field[float]
        | Field[bool]
        | Field[datetime]
        | Field[bytes]
        | Field[list[str]]
        | Field[list[int]]
        | Field[list[float]]
        | Field[list[bool]]
        | Field[list[datetime]]
        | Field[list[bytes]]
        | Schema,
    ]:
        return self._fields.items()

    def __getitem__(
        self,
        key: str,
    ) -> (
        Field[str]
        | Field[int]
        | Field[float]
        | Field[bool]
        | Field[datetime]
        | Field[bytes]
        | Field[list[str]]
        | Field[list[int]]
        | Field[list[float]]
        | Field[list[bool]]
        | Field[list[datetime]]
        | Field[list[bytes]]
        | Schema
    ):
        return self._fields[key]

    def __contains__(self, key: str) -> bool:
        return key in self._fields

    def __repr__(self) -> str:
        return (
            f"Schema(name={self._name!r}, "
            f"description={self._description!r}, "
            f"entries={{{', '.join(f'{entry!r}' for entry in self._fields.values()) if self._fields else ''}}})"  # noqa: E501
        )
