from __future__ import annotations

from typing import Generic, TypeVar

from ..members.field import Field
from .base import Definition, TomlScalar

ScalarValueT = TypeVar("ScalarValueT", bound=TomlScalar)


class Scalar(Field[ScalarValueT], Definition[ScalarValueT], Generic[ScalarValueT]):
    __slots__ = ()

    def __init__(
        self,
        name: str,
        description: str,
        /,
        *,
        required: bool,
        default: ScalarValueT | None,
    ) -> None:
        Field.__init__(self, name, description, required, self, default)
