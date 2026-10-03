from __future__ import annotations

from abc import abstractmethod
from typing import Generic, TypeVar, final

from typing_extensions import override

from confflow.core.errors import ValidationError
from confflow.core.schemas.base import Schema

ItemT = TypeVar(name="ItemT")


class Array(Schema[list[ItemT]], Generic[ItemT]):
    @override
    @final
    def validate(self, value: list[ItemT], /) -> None:
        for index, item in enumerate(iterable=value):
            try:
                self._validate_item(item)
            except ValidationError as error:
                error.prepend_path(index)
                raise
            except (TypeError, ValueError, RuntimeError) as error:
                raise ValidationError(
                    str(error),
                    path=(index,),
                    value=item,
                    expected=type(self).__name__,
                ) from error

    @abstractmethod
    def _validate_item(self, value: ItemT, /) -> None: ...

    @override
    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}("
            f"name={self.name!r}, "
            f"description={self.description!r}, "
            f"optional={self.optional!r})"
        )
