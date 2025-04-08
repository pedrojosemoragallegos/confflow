from collections import defaultdict
from typing import Dict, List

from pydantic import BaseModel

from ..utils.types import SchemaGroup, SchemaType


class ExclusiveSchemaManager:
    def __init__(self) -> None:
        self._exclusive_groups: Dict[str, SchemaGroup] = defaultdict(list)

    def add_to_group(self, group_name: str, schema: SchemaType) -> None:
        self._exclusive_groups[group_name].append(schema)

    @property
    def exclusive_groups(self) -> List[SchemaGroup]:
        return list(self._exclusive_groups.values())

    def validate(self, schemas: List[BaseModel]) -> None:
        for group in self.exclusive_groups:
            active = [s for s in schemas if isinstance(s, tuple(group))]
            if len(active) > 1:
                raise ValueError(
                    f"Conflict in exclusivity group: {[cls.__name__ for cls in group]}"
                )
