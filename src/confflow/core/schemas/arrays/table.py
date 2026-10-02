from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Final

from typing_extensions import override

from .base import Array

if TYPE_CHECKING:
    from confflow.core.schemas.table import Table as TableSchema


class Table(Array[Mapping[str, object]]):
    __slots__ = ("__table",)

    def __init__(
        self,
        name: str,
        description: str | None,
        table: TableSchema,
        /,
        *,
        optional: bool = False,
    ) -> None:
        super().__init__(name, description, optional=optional)

        self.__table: Final[TableSchema] = table

    @property
    def table(self) -> TableSchema:
        return self.__table

    @override
    def _validate_item(self, value: Mapping[str, object], /) -> None:
        self.__table.validate(value)

    @override
    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}("
            f"name={self.name!r}, "
            f"description={self.description!r}, "
            f"optional={self.optional!r}, "
            f"table={self.__table!r})"
        )
