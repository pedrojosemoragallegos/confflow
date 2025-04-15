from abc import ABC, abstractmethod

from ...common.types import Schema


class BaseRule(ABC):
    def __init__(self) -> None:
        self._schemas: set[Schema] = set()

    @abstractmethod
    def is_violated(
        self,
        active_schemas: list[Schema],
    ) -> bool: ...

    @abstractmethod
    def __eq__(self, other) -> bool: ...

    @abstractmethod
    def __hash__(self) -> int: ...

    @property
    def referenced_schemas(self) -> set[Schema]:
        return self._schemas.copy()
