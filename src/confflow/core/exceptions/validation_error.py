from __future__ import annotations

from typing import Final

from typing_extensions import override


class ValidationError(Exception):
    __slots__ = ("__path",)

    @override
    def __init__(  # ty: ignore[invalid-method-override]
        self, message: str, path: tuple[str | int, ...]
    ) -> None:
        super().__init__(message)
        self.__path: Final[tuple[str | int, ...]] = path

    @property
    def path(self) -> tuple[str | int, ...]:
        return self.__path

    @override
    def __repr__(self) -> str:
        return f"{type(self).__name__}({str(self)!r}, path={self.__path!r})"
