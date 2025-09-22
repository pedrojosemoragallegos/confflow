from __future__ import annotations

import typing

from confflow.mixins import IPythonMixin

from .entry import Entry

if typing.TYPE_CHECKING:
    from collections.abc import ItemsView, KeysView, ValuesView

    from confflow.types import EntryTypes, ValueTypes

    ConfigOrEntry: typing.TypeAlias = EntryTypes | "Config"


class Config(IPythonMixin):
    def __init__(
        self,
        name: str,
        description: str,
        *items: ConfigOrEntry,
    ) -> None:
        if not items:
            raise ValueError("Config must contain at least one configuration item")  # noqa: EM101, TRY003

        self._name: str = name
        self._description: str = description
        self._items: dict[str, ConfigOrEntry] = {item.name: item for item in items}

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

    def __getitem__(
        self,
        key: str,
    ) -> str | ValueTypes | Config:
        config_or_entry: ConfigOrEntry = self._items[key]
        if isinstance(config_or_entry, Entry):
            return config_or_entry.value
        return config_or_entry

    def __contains__(self, key: str) -> bool:
        return key in self._items

    def __repr__(self) -> str:
        return f"Config(name={self._name!r}, items={self._items!r})"

    def __dir__(self) -> list[str]:
        return [attr for attr in dir(type(self)) if not attr.startswith("_")]
