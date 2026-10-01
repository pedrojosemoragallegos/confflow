from __future__ import annotations

from abc import abstractmethod

from typing_extensions import override

from confflow.core.schemas.base import Schema
from confflow.core.schemas.exceptions import SchemaError


class Array(Schema):
    @override
    def validate(self, value: object, /) -> None:
        super().validate(value)

        if not isinstance(value, list):
            raise SchemaError("array value must be a list")

        for item in value:
            self._validate_item(item)

    @abstractmethod
    def _validate_item(self, value: object, /) -> None: ...

    @override
    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}(name={self.name!r}, "
            f"description={self.description!r}, "
            f"optional={self.optional!r})"
        )
