from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Iterator, Union

from ..schema import Schema


class Group(ABC):
    def __init__(self, *schemas: Schema):
        if not schemas:
            raise ValueError("Group must contain at least one schema")
        self._schemas: tuple[Schema, ...] = schemas
        self._names: set[str] = {schema.name for schema in schemas}

    @property
    def schemas(self) -> tuple[Schema, ...]:
        return self._schemas

    @property
    def names(self) -> set[str]:
        return self._names

    def __iter__(self) -> Iterator[Schema]:
        return iter(self._schemas)

    def __len__(self) -> int:
        return len(self._schemas)

    def __contains__(self, schema: Union[Schema, str]) -> bool:
        if isinstance(schema, str):
            return schema in self._names
        return schema in self._schemas

    @abstractmethod
    def validate(self, present_schemas: list[str], file_path: Union[str, Path]): ...

    @property
    @abstractmethod
    def template_comment(self) -> str: ...

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({[schema.name for schema in self._schemas]})"


class MutualExclusive(Group):
    def validate(self, present_schemas: list[str], file_path: Union[str, Path]):
        if len(present_schemas) == 0:
            group_names: list[str] = list(self.names)
            raise ValueError(
                f"Missing required group section in config file {file_path}. "
                f"Must include exactly one of: {group_names}"
            )
        elif len(present_schemas) > 1:
            raise ValueError(
                f"Multiple mutually exclusive sections found in config file {file_path}: {present_schemas}. "
                f"Group allows only one of: {list(self.names)}"
            )

    @property
    def template_comment(self) -> str:
        return f"# ╔════════════════════════════════════════════════════════════╗\n# ║ MUTUALLY EXCLUSIVE: Choose ONE of the following {len(self)} options  ║\n# ╚════════════════════════════════════════════════════════════╝"
