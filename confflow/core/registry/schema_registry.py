from typing import OrderedDict, TypeAlias

from pydantic import BaseModel

from ...common.types import Schema, SchemaName

SchemaMap: TypeAlias = OrderedDict[SchemaName, Schema]


class SchemaRegistry:
    def __init__(self) -> None:
        self._schema_map: SchemaMap = SchemaMap()

    def register(self, schema: Schema) -> None:
        schema_name: SchemaName = schema.__name__

        if schema_name in self._schema_map:
            raise ValueError(f"Schema '{schema_name}' is already registered.")

        self._schema_map[schema_name] = schema

    @property
    def schema_types(self) -> list[BaseModel]:
        return list(self._schema_map.values())

    @property
    def schema_names(self) -> list[SchemaName]:
        return list(self._schema_map.keys())

    def __getitem__(self, name: SchemaName) -> BaseModel:
        return self._schema_map[name]

    def __contains__(self, name: SchemaName) -> bool:
        return name in self._schema_map
