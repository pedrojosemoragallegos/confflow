from collections import OrderedDict
from typing import Union

from .fields import (
    BooleanField,
    BytesField,
    FloatField,
    IntegerField,
    ListField,
    MappingField,
    SetField,
    StringField,
    TimestampField,
)

FieldType = Union[
    BooleanField,
    BytesField,
    FloatField,
    IntegerField,
    ListField,
    MappingField,
    SetField,
    StringField,
    TimestampField,
]


class ConfigSchemaBuilder:
    def __init__(self):
        self._field_defs: OrderedDict[str, FieldType] = OrderedDict()

    def add_field(self, field: FieldType) -> "ConfigSchemaBuilder":
        if field.name in self._field_defs:
            raise ValueError(f"Field '{field.name}' already added to schema.")
        self._field_defs[field.name] = field
        return self

    def build(self) -> "Config":
        config = Config()
        for field in self._field_defs.values():
            # Clone the field (not value) to ensure fresh instantiation
            field_copy = copy.deepcopy(field)
            field_copy._value = None  # clear values from schema phase
            config.add_field(field_copy)
        return config

    def schema_fields(self) -> OrderedDict[str, Field]:
        return copy.deepcopy(self._field_defs)
