from __future__ import annotations

from typing import TYPE_CHECKING

from typing_extensions import override

from confflow.core.shared import TOMLValue, is_toml_value

from .base import Field

if TYPE_CHECKING:
    from confflow.core.schema import Schema


class ArrayOfTables(Field[list[dict[str, TOMLValue]]]):  # ty: ignore[invalid-type-arguments]
    __slots__ = ("_schema",)

    def __init__(
        self,
        name: str,
        description: str,
        schema: Schema,
        /,
        *,
        required: bool = False,
        default: list[dict[str, TOMLValue]] | None = None,
    ) -> None:
        self._schema: Schema = schema

        super().__init__(
            name,
            description,
            required=required,
            default=default,  # ty: ignore[invalid-argument-type]
        )

        if self._default is not None:
            for index, row in enumerate(self._default):
                schema._prepare(row, f"{name}[{index}]")  # noqa: SLF001

    @property
    def schema(self) -> Schema:
        return self._schema

    @override
    def _typecheck(self, value: object, /) -> bool:
        return type(value) is list and all(
            type(item) is dict and is_toml_value(item) for item in value
        )
