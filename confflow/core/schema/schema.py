from collections import OrderedDict
from datetime import datetime
from typing import Union

from .field import Field


class Schema:
    def __init__(self, name: str, description: str):
        self._name = name
        self._description = description
        self._fields: OrderedDict[
            str,
            Union[
                Field[
                    Union[
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
                    ]
                ],
                "Schema",
            ],
        ] = OrderedDict()

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    @property
    def fields(self):  # TODO correct typing
        return self._fields.values()

    def add(self, _FieldOrSchema: Union[Field, "Schema"]) -> "Schema":
        self._fields[_FieldOrSchema.name] = _FieldOrSchema

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

    # TODO maybe remove here  as mixin or so
    def _ipython_key_completions_(self) -> list[str]:
        return list(self._fields.keys())

    def __repr__(self) -> str:
        return (
            f"Schema(name={self._name!r}, "
            f"description={self._description!r}, "
            f"entries={{{', '.join(f'{entry!r}' for name, entry in self._fields.items()) if self._fields else ''}}})"
        )
