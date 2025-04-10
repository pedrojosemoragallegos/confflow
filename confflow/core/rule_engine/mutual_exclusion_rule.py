from ...utils.types import Schema
from .base_rule import BaseRule


class MutualExclusionRule(BaseRule):
    def __init__(self, *exclusive_schemas: Schema):
        super().__init__()
        self._schemas = set(exclusive_schemas)

    def is_violated(self, active_schemas: list[Schema]) -> bool:
        overlaped_schemas: set[Schema] = self._schemas.intersection(active_schemas)

        return len(overlaped_schemas) > 1

    def __eq__(self, other) -> bool:
        if not isinstance(other, MutualExclusionRule):
            return NotImplemented
        return self._schemas == other._schemas

    def __hash__(self) -> int:
        return hash(frozenset(self._schemas))

    @property
    def referenced_schemas(self) -> set[Schema]:
        return self._schemas.copy()

    def __repr__(self) -> str:
        schemas_repr: str = ", ".join(
            schema.__name__ for schema in sorted(self._schemas, key=str)
        )

        return f"{self.__class__.__name__}(exclusive_schemas=[{schemas_repr}])"
