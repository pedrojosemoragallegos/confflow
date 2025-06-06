from collections import OrderedDict
from collections.abc import ItemsView, Iterable, Iterator, KeysView, ValuesView
from datetime import datetime
from typing import Optional, final

from .field_constraint import FieldConstraint
from .field_factory import Field as FieldFactory
from .field_values import FieldValue
from .fields import (
    BooleanField,
    BytesField,
    Field,
    FloatField,
    IntegerField,
    ListField,
    MappingField,
    SetField,
    StringField,
    TimestampField,
)


class FieldEntry:
    def __init__(self, field: Field, default_value=None, required=False):
        self._field = field
        self._default_value = default_value
        self._required = required

        if isinstance(field, StringField) and isinstance(
            default_value, (str, type(None))
        ):
            ...
        elif isinstance(field, IntegerField) and isinstance(
            default_value, (int, type(None))
        ):
            ...
        elif isinstance(field, FloatField) and isinstance(
            default_value, (float, type(None))
        ):
            ...
        elif isinstance(field, BooleanField) and isinstance(
            default_value, (bool, type(None))
        ):
            ...
        elif isinstance(field, TimestampField) and isinstance(
            default_value, (datetime, type(None))
        ):
            ...
        elif isinstance(field, BytesField) and isinstance(
            default_value, (bytes, type(None))
        ):
            ...
        elif isinstance(field, ListField) and isinstance(
            default_value, (list, type(None))
        ):
            if default_value:
                all(
                    isinstance(
                        item,
                        (str, int, float, bool, datetime, bytes),
                    )
                    for item in default_value
                )
        elif isinstance(field, MappingField) and isinstance(
            default_value, (dict, type(None))
        ):
            if default_value:
                all(
                    isinstance(
                        item,
                        (str, int, float, bool, datetime, bytes),
                    )
                    for item in default_value
                )
        elif isinstance(field, SetField) and isinstance(
            default_value, (set, type(None))
        ):
            if default_value:
                all(
                    isinstance(
                        item,
                        (str, int, float, bool, datetime, bytes),
                    )
                    for item in default_value
                )
        else:
            raise ValueError("Passed value and default_value aren't same type.")

    @property
    def name(self) -> str:
        return self._field.name

    @property
    def description(self) -> str:
        return self._field.description

    @property
    def value(self):
        return self._field.value

    @property
    def required(self) -> bool:
        return self._required

    @property
    def default_value(self) -> bool:
        return self._default_value


@final
class Config:
    def __init__(self, name: str, description: Optional[str] = None):
        self._name: str = name
        self._description: str = description or ""
        self._fields: OrderedDict[str, Field] = OrderedDict()

    def addField(
        self,
        value: FieldValue,
        *,
        name: str,
        description: Optional[str] = None,
        default_value: Optional[FieldValue] = None,
        required: bool = False,
        constraints: Optional[Iterable[FieldConstraint[FieldValue]]] = None,
    ) -> "Config":
        if name in self._fields:
            raise ValueError(f"Field with name '{name}' already exists.")

        field = FieldFactory(
            value=value,
            name=name,
            description=description,
            constraints=constraints,
        )

        self._fields[name] = FieldEntry(
            field=field,
            default_value=default_value,
            required=required,
        )

        return self

    def keys(self) -> KeysView[str]:
        return self._fields.keys()

    def values(self) -> ValuesView[Field]:
        return self._fields.values()

    def items(self) -> ItemsView[str, Field]:
        return self._fields.items()

    def __getitem__(self, key: str) -> Field:
        return self._fields[key]

    def __contains__(self, key: str) -> bool:
        return key in self._fields

    def __iter__(self) -> Iterator[str]:
        return iter(self._fields)

    def __len__(self) -> int:
        return len(self._fields)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"name={self._name!r}, "
            f"description={self._description!r}, "
            f"fields={[field for field in self._fields.values()]!r})"
        )

    # Only for iPython # TODO maybe remove here add as mixin or so
    def _ipython_key_completions_(self) -> list[str]:
        return list(self._fields.keys())
