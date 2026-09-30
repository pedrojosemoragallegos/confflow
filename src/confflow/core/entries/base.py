from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Final

from ..definitions._validators import validate_name


class Entry(ABC):
    __slots__ = ("__description", "__name", "__optional")

    def __init__(
        self, name: str, description: str | None, /, *, optional: bool
    ) -> None:
        validate_name(value=name, label="entry name")

        self.__name: Final[str] = name
        self.__description: Final[str | None] = description
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
    def validate(self, value: object) -> None: ...

    @abstractmethod
    def __repr__(self) -> str: ...
