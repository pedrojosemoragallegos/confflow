from __future__ import annotations

from typing import TYPE_CHECKING, Final

from typing_extensions import override

from .base import Array

if TYPE_CHECKING:
    from confflow.core.schemas.table import Table as TableSchema


class Table(Array):
    __slots__ = ("__table",)

    def __init__(
        self,
        name: str,
        description: str | None = None,
        /,
        *,
        optional: bool = False,
        table: TableSchema,
    ) -> None:
        super().__init__(name, description, optional=optional)

        self.__table: Final[TableSchema] = table

    @property
    def table(self) -> TableSchema:
        return self.__table

    @override
    def _validate_item(self, value: object, /) -> None:
        self.__table.validate(value)

    @override
    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}(name={self.name!r}, "
            f"description={self.description!r}, "
            f"optional={self.optional!r}, "
            f"table={self.__table!r})"
        )
