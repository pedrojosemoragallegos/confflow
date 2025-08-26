from __future__ import annotations

from collections import OrderedDict
from collections.abc import Iterable
from typing import (
    ItemsView,
    KeysView,
    Optional,
    TypeVar,
    Union,
    ValuesView,
)

from confflow.mixins import IPythonMixin
from confflow.types import Value

from .entry import Constraint, Entry

ConfigEntry = Entry[Value]
ConfigOrEntry = Union[ConfigEntry, "Config"]

T = TypeVar("T", bound=Value)


class Config(IPythonMixin):
    def __init__(self, name: str, description: Optional[str] = None):
        self._name: str = name
        self._description: str = description or ""
        self._entries: OrderedDict[str, ConfigOrEntry] = OrderedDict()
        self._defaults: dict[str, Optional[Value]] = {}
        self._required: dict[str, bool] = {}

    def Entry(
        self,
        value: T,
        *,
        name: str,
        description: Optional[str] = None,
        default_value: Optional[T] = None,
        required: bool = False,
        constraints: Optional[Iterable[Constraint[T]]] = None,
    ) -> "Config":
        if name in self._entries:
            raise ValueError(f"Entry with name '{name}' already exists.")

        if default_value is not None and type(value) is not type(
            default_value
        ):  # TODO really needed?
            raise ValueError(
                f"Type mismatch: 'value' ({type(value)}) and 'default_value' ({type(default_value)})"
            )

        entry = Entry[T](
            value=value,
            name=name,
            description=description,
            constraints=constraints,
        )

        self._entries[name] = entry
        self._defaults[name] = default_value
        self._required[name] = required
        return self

    def SubConfig(self, name: str, config: "Config") -> "Config":
        if name in self._entries:
            raise ValueError(f"Entry with name '{name}' already exists.")
        self._entries[name] = config
        return self

    def __len__(self) -> int:
        return len(self._entries)

    def keys(self) -> KeysView[str]:
        return self._entries.keys()

    def values(self) -> ValuesView[ConfigOrEntry]:
        return self._entries.values()

    def items(self) -> ItemsView[str, ConfigOrEntry]:
        return self._entries.items()

    def __getitem__(self, key: str) -> Union[Value, "Config"]:
        entry = self._entries[key]
        if isinstance(entry, Entry):
            return entry.value
        return entry

    def __contains__(self, key: str) -> bool:
        return key in self._entries

    def __repr__(self) -> str:
        entries_str = ", ".join(self._entries.keys()) if self._entries else "empty"
        return f"Config(name={self._name!r}, entries=[{entries_str}])"
