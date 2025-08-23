from collections import OrderedDict
from collections.abc import Iterable
from datetime import datetime
from typing import Optional, TypeVar, Union

from .entry import Constraint, Entry

T = TypeVar("T", bound=Union[str, int, float, bool, datetime, bytes])


class Config:
    def __init__(self, name: str, description: Optional[str] = None):
        self._name: str = name
        self._description: str = description or ""
        self._entries: OrderedDict[
            str, Union[Entry[Union[str, int, float, bool, datetime, bytes]], Config]
        ] = OrderedDict()
        self._defaults: dict[
            str, Optional[Union[str, int, float, bool, datetime, bytes]]
        ] = {}
        self._required: dict[str, bool] = dict()

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

        if default_value is not None and type(value) is not type(default_value):
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

    def keys(self):  # TODO add return type
        return self._entries.keys()

    def values(self):  # TODO add return type
        return self._entries.values()

    def items(self):  # TODO add return type
        return self._entries.items()

    def __getitem__(self, key: str):  # TODO add return type
        entry = self._entries[key]
        if isinstance(entry, Entry):
            return entry.value

        return entry

    def __contains__(self, key: str):  # TODO add return type
        return key in self._entries

    # Only for iPython # TODO maybe remove here add as mixin or so
    def _ipython_key_completions_(self) -> list[str]:
        return list(self._entries.keys())

    def __repr__(self) -> str:
        return f"Config(name={self._name!r}, entries=[{', '.join(self._entries.keys()) if self._entries else 'empty'}])"
