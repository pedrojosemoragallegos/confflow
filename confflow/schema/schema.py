from __future__ import annotations

from collections import OrderedDict
from typing import Union

from confflow.mixins import IPythonMixin
from confflow.types import Value

from .field import Field


class Schema(IPythonMixin):
    def __init__(self, name: str, *, description: str):
        self._name: str = name
        self._description: str = description
        self._fields: OrderedDict[str, Union[Field[Value], Schema]] = OrderedDict()

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    @property
    def fields(self):  # TODO correct typing
        return self._fields.values()

    from typing import overload

    @overload
    def add(self, item: Field[Value]) -> Schema: ...

    @overload
    def add(self, item: Schema) -> Schema: ...

    def add(self, item: Union[Field[Value], Schema]) -> Schema:
        if isinstance(item, Schema):
            if item == self:
                raise ValueError("Schema cannot be added to itself")
            self._fields.update(item._fields)
        else:  # Field
            self._fields[item.name] = item
        return self

    def keys(self):  # TODO correct typing
        return self._fields.keys()

    def values(self):  # TODO correct typing
        return self._fields.values()

    def items(self):  # TODO correct typing
        return self._fields.items()

    def __getitem__(self, key: str):  # TODO correct typing
        return self._fields[key]

    def __contains__(self, key: str) -> bool:
        return key in self._fields

    def __repr__(self) -> str:
        return (
            f"Schema(name={self._name!r}, "
            f"description={self._description!r}, "
            f"entries={{{', '.join(f'{entry!r}' for entry in self._fields.values()) if self._fields else ''}}})"
        )
