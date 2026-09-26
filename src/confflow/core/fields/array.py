from __future__ import annotations

from typing import ClassVar, Generic

from typing_extensions import override

from confflow.core.shared import ConfigurationError, V

from .base import Field


class Array(Field[list[V]], Generic[V]):  # ty: ignore[invalid-type-arguments]
    option_names: ClassVar[tuple[str, ...]] = ("min_length", "max_length")

    __slots__ = ("_element", "_max_length", "_min_length")

    def __init__(
        self,
        name: str,
        description: str,
        /,
        *,
        element: Field[V],
        required: bool = False,
        default: list[V] | None = None,
        min_length: int | None = None,
        max_length: int | None = None,
    ) -> None:
        if min_length is not None and min_length < 0:
            msg = "min_length must be non-negative"
            raise ValueError(msg)

        if max_length is not None and max_length < 0:
            msg = "max_length must be non-negative"
            raise ValueError(msg)

        if (
            min_length is not None
            and max_length is not None
            and min_length > max_length
        ):
            msg = "min_length cannot exceed max_length"
            raise ValueError(msg)

        self._element: Field[V] = element
        self._min_length: int | None = min_length
        self._max_length: int | None = max_length

        super().__init__(name, description, required=required, default=default)

    @property
    def element(self) -> Field[V]:
        return self._element

    @property
    def min_length(self) -> int | None:
        return self._min_length

    @property
    def max_length(self) -> int | None:
        return self._max_length

    @override
    def _typecheck(self, value: object, /) -> bool:
        return type(value) is list

    @override
    def validate(self, value: object, path: str, /) -> list[V]:
        value: list[V] = super().validate(value, path)

        if self.min_length is not None and len(value) < self.min_length:
            raise ConfigurationError(path, f"length must be >= {self.min_length}")

        if self.max_length is not None and len(value) > self.max_length:
            raise ConfigurationError(path, f"length must be <= {self.max_length}")

        return [
            self.element.validate(item, f"{path}[{index}]")
            for index, item in enumerate(value)
        ]
