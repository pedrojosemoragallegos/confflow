from __future__ import annotations

import typing
from datetime import datetime

from .config.entry import Entry
from .schema.field import Field

EntryTypes: typing.TypeAlias = (
    Entry[str]
    | Entry[int]
    | Entry[float]
    | Entry[bool]
    | Entry[datetime]
    | Entry[bytes]
    | Entry[list[str]]
    | Entry[list[int]]
    | Entry[list[float]]
    | Entry[list[bool]]
    | Entry[list[datetime]]
    | Entry[list[bytes]]
)

FieldTypes: typing.TypeAlias = (
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
)

ValueTypes: typing.TypeAlias = (
    list[str]
    | list[int]
    | list[float]
    | list[bool]
    | list[datetime]
    | list[bytes]
    | str
    | int
    | float
    | bool
    | datetime
    | bytes
)


YAMLValue: typing.TypeAlias = (
    str | int | float | bool | None | dict[str, "YAMLValue"] | list["YAMLValue"]
)
YAMLDict: typing.TypeAlias = dict[str, YAMLValue]
YAMLList: typing.TypeAlias = list[YAMLValue]
YAMLContent: typing.TypeAlias = YAMLDict | YAMLList | str | int | float | bool | None
