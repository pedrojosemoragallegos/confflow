from __future__ import annotations

from abc import ABC, abstractmethod
from re import compile as compile_pattern
from typing import Final, Generic, TypeVar

ValueT = TypeVar(name="ValueT")  # TODO: not bounded to any specific type
_NAME_PATTERN = compile_pattern(pattern=r"[A-Za-z0-9_-]+")


class Schema(ABC, Generic[ValueT]):
    __slots__ = ("__description", "__name", "__optional")

    def __init__(self, name: str, description: str, /, *, optional: bool) -> None:
        if type(name) is not str or _NAME_PATTERN.fullmatch(string=name) is None:
            raise ValueError("Name must contain only ASCII letters, digits, '_' or '-'")

        self.__name: Final[str] = name
        self.__description: Final[str | None] = description if description else None
        self.__optional: Final[bool] = optional

    @property
    def name(self) -> str:
        return self.__name

    @property
    def description(self) -> str | None:
        return self.__description

    @property
    def optional(self) -> bool:
        return self.__optional

    @abstractmethod
    def validate(self, value: ValueT, /) -> None: ...

    @abstractmethod
    def __repr__(self) -> str: ...
