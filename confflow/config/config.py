from __future__ import annotations

from collections import OrderedDict
from typing import (
    ItemsView,
    KeysView,
    TypeVar,
    Union,
    ValuesView,
)

from confflow.mixins import IPythonMixin
from confflow.types import Value

from .entry import Entry

ConfigOrEntry = Union[Entry[Value], "Config"]
T = TypeVar("T", bound=Value)


class Config(IPythonMixin):
    def __init__(
        self,
        name: str,
        description: str,
        *items: ConfigOrEntry,
    ):
        if not len(items):
            raise ValueError("Config must contain at least one configuration item")
        self._name: str = name
        self._description: str = description
        self._items: OrderedDict[str, ConfigOrEntry] = OrderedDict(
            (item.name, item) for item in items
        )

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    def __len__(self) -> int:
        return len(self._items)

    def keys(self) -> KeysView[str]:
        return self._items.keys()

    def values(self) -> ValuesView[ConfigOrEntry]:
        return self._items.values()

    def items(self) -> ItemsView[str, ConfigOrEntry]:
        return self._items.items()

    def __getitem__(self, key: str) -> Union[Value, "Config"]:
        entry: Union["Config", Entry[Value]] = self._items[key]
        if isinstance(entry, Entry):
            return entry.value
        return entry

    def __contains__(self, key: str) -> bool:
        return key in self._items

    def __repr__(self) -> str:
        return f"Config(name={self._name!r}, items={self._items!r})"

    def __dir__(self):
        return [attr for attr in dir(type(self)) if not attr.startswith("_")]
