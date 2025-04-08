from collections import defaultdict
from typing import Dict, List, Type

from pydantic import BaseModel


class ExclusiveSchemaManager:
    def __init__(self):
        self._exclusive_groups: Dict[str, List[Type[BaseModel]]] = defaultdict(list)

    def add_to_group(self, group_name: str, schema: Type[BaseModel]):
        self._exclusive_groups[group_name].append(schema)

    @property
    def exclusive_groups(self) -> List[List[Type[BaseModel]]]:
        return list(self._exclusive_groups.values())

    def validate(self, schemas: List[BaseModel]):
        for group in self.exclusive_groups:
            active = [s for s in schemas if isinstance(s, tuple(group))]
            if len(active) > 1:
                raise ValueError(
                    f"Conflict in exclusivity group: {[cls.__name__ for cls in group]}"
                )
