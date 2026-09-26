from __future__ import annotations

from typing import TYPE_CHECKING

from typing_extensions import override

from confflow.core.shared import TOMLValue, is_toml_value

from .base import Field

if TYPE_CHECKING:
    from confflow.core.schema import Schema


class _Table(Field[dict[str, TOMLValue]]):
    __slots__ = ("_schema",)

    def __init__(self, schema: Schema, /, *, required: bool = False) -> None:
        self._schema: Schema = schema

        super().__init__(schema.name, schema.description, required=required)

    @property
    def schema(self) -> Schema:
        return self._schema

    @override
    def _typecheck(self, value: object, /) -> bool:
        return type(value) is dict and is_toml_value(value)
