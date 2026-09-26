from __future__ import annotations

import re
from typing import ClassVar

from typing_extensions import override

from confflow.core.shared import ConfigurationError

from .base import Field


class String(Field[str]):
    option_names: ClassVar[tuple[str, ...]] = ("min_length", "max_length", "pattern")

    __slots__ = ("_compiled_pattern", "_max_length", "_min_length", "_pattern")

    def __init__(
        self,
        name: str,
        description: str,
        /,
        *,
        required: bool = False,
        default: str | None = None,
        min_length: int | None = None,
        max_length: int | None = None,
        pattern: str | None = None,
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

        self._min_length: int | None = min_length
        self._max_length: int | None = max_length
        self._pattern: str | None = pattern
        self._compiled_pattern: re.Pattern | None = (
            re.compile(pattern) if pattern is not None else None
        )

        super().__init__(name, description, required=required, default=default)

    @property
    def min_length(self) -> int | None:
        return self._min_length

    @property
    def max_length(self) -> int | None:
        return self._max_length

    @property
    def pattern(self) -> str | None:
        return self._pattern

    @override
    def _typecheck(self, value: object, /) -> bool:
        return type(value) is str

    @override
    def validate(self, value: object, path: str, /) -> str:
        value: str = super().validate(value, path)

        if self.min_length is not None and len(value) < self.min_length:
            raise ConfigurationError(path, f"length must be >= {self.min_length}")

        if self.max_length is not None and len(value) > self.max_length:
            raise ConfigurationError(path, f"length must be <= {self.max_length}")

        if (
            self._compiled_pattern is not None
            and self._compiled_pattern.fullmatch(string=value) is None
        ):
            raise ConfigurationError(path, f"must match {self.pattern!r}")

        return value
