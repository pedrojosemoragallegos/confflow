from __future__ import annotations

import typing
from abc import ABC, abstractmethod

if typing.TYPE_CHECKING:
    from collections.abc import Iterator
    from pathlib import Path

    from confflow.schema import Schema


class Group(ABC):
    def __init__(self, *schemas: Schema) -> None:
        if not schemas:
            raise ValueError("Group must contain at least one schema")  # noqa: EM101, TRY003
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

    def __contains__(self, schema: Schema | str) -> bool:
        if isinstance(schema, str):
            return schema in self._names
        return schema in self._schemas

    @abstractmethod
    def validate(self, present_schemas: list[str], file_path: str | Path) -> None: ...

    @property
    @abstractmethod
    def template_comment(self) -> str: ...

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({[schema.name for schema in self._schemas]})"


class MutualExclusive(Group):
    def validate(self, present_schemas: list[str], file_path: str | Path) -> None:
        if len(present_schemas) == 0:
            group_names: list[str] = list(self.names)
            raise ValueError(  # noqa: TRY003
                f"Missing required group section in config file {file_path}. "  # noqa: EM102
                f"Must include exactly one of: {group_names}",
            )
        if len(present_schemas) > 1:
            raise ValueError(  # noqa: TRY003
                f"Multiple mutually exclusive sections found in config file {file_path}: {present_schemas}. "  # noqa: E501, EM102
                f"Group allows only one of: {list(self.names)}",
            )

    @property
    def template_comment(self) -> str:
        return f"# ╔════════════════════════════════════════════════════════════╗\n# ║ MUTUALLY EXCLUSIVE: Choose ONE of the following {len(self)} options  ║\n# ╚════════════════════════════════════════════════════════════╝"  # noqa: E501
