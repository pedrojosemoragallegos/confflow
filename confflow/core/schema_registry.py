from typing import Dict, List, Optional, Type

from pydantic import BaseModel

from ..utils.types import SchemaMap, SchemaName


class SchemaRegistry:
    def __init__(self):
        self._schema_map: SchemaMap = SchemaMap()
        self._schema_descriptions: Dict[SchemaName, str] = {}

    def register(self, schema: Type[BaseModel], description: Optional[str] = None):
        name: SchemaName = schema.__name__

        if name in self._schema_map:
            raise ValueError(f"Schema '{name}' is already registered.")

        self._schema_map[name] = schema
        if description:
            self._schema_descriptions[name] = description

    @property
    def schemas(self) -> List[BaseModel]:
        return list(self._schema_map.values())

    def get_description(self, name: SchemaName) -> Optional[str]:
        return self._schema_descriptions.get(name)

    def __getitem__(self, name: SchemaName) -> BaseModel:
        return self._schema_map[name]

    def __contains__(self, name: SchemaName) -> bool:
        return name in self._schema_map
