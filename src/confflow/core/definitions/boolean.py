from __future__ import annotations

from typing_extensions import override

from ..exceptions import InvalidValueError
from .scalar import Scalar


class Boolean(Scalar[bool]):
    __slots__ = ()

    @override
    def __init__(
        self,
        name: str,
        description: str = "",
        /,
        *,
        required: bool = False,
        default: bool | None = None,
    ) -> None:
        super().__init__(name, description, required=required, default=default)

    @property
    @override
    def value_type(self) -> type[bool]:
        return bool

    @override
    def validate(self, value: object, path: tuple[str | int, ...]) -> None:
        if type(value) is not bool:
            raise InvalidValueError("expected a boolean", path)

    @override
    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}(name={self.name!r}, "
            f"description={self.description!r}, required={self.required!r}, "
            f"default={self.default!r})"
        )
