from collections import OrderedDict
from collections.abc import Iterable
from typing import Optional, TypeVar

from confflow.types import Value

from .field.field import Constraint, Field

T = TypeVar("T", bound=Value)


class Config:
    def __init__(self, name: str, description: Optional[str] = None):
        self._name: str = name
        self._description: str = description or ""
        self._fields: OrderedDict[str, Field[Value]] = OrderedDict()
        self._defaults: list[Optional[Value]] = list()
        self._requirets: list[bool] = list()

    def addField(
        self,
        value: T,
        *,
        name: str,
        description: Optional[str] = None,
        default_value: Optional[T] = None,
        required: bool = False,
        constraints: Optional[Iterable[Constraint[T]]] = None,
    ) -> "Config":
        if name in self._fields:
            raise ValueError(f"Field with name '{name}' already exists.")

        if default_value:
            if type(value) is not type(default_value):
                raise ValueError(
                    f"Type of 'value' {value}: {type(value)} and 'default_value' {default_value}: {type(default_value)} don't match"
                )

        self._fields[name] = Field[T](
            value=value, name=name, description=description, constraints=constraints
        )

        self._defaults.append(default_value)
        self._requirets.append(required)

        return self

    def __len__(self) -> int:
        return len(self._fields)

    def keys(self):  # TODO add return type
        return self._fields.keys()

    def values(self):  # TODO add return type
        return self._fields.values()

    def items(self):  # TODO add return type
        return self._fields.items()

    def __getitem__(self, key: str):  # TODO add return type
        return self._fields[key].value

    def __contains__(self, key: str):  # TODO add return type
        return key in self._fields

    # Only for iPython # TODO maybe remove here add as mixin or so
    def _ipython_key_completions_(self) -> list[str]:
        return list(self._fields.keys())
