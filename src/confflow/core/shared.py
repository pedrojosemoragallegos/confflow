from __future__ import annotations

import re
from datetime import date, datetime, time
from typing import TYPE_CHECKING, TypeVar

if TYPE_CHECKING:
    from typing import Final, TypeAlias

TOMLScalar: TypeAlias = str | int | float | bool | date | time | datetime
TOMLValue: TypeAlias = TOMLScalar | list["TOMLValue"] | dict[str, "TOMLValue"]
T_co = TypeVar(name="T_co", bound=TOMLValue, covariant=True)
S = TypeVar(name="S", bound=TOMLScalar)
V = TypeVar(name="V", bound=TOMLValue)

_BARE_KEY_RE = re.compile(r"[A-Za-z0-9_-]+")

TOML_INT_MIN: Final[int] = -(2**63)
TOML_INT_MAX: Final[int] = 2**63 - 1


def validate_name(name: str, /) -> None:
    if not name:
        msg = "names must not be empty"
        raise ValueError(msg)
    if _BARE_KEY_RE.fullmatch(name) is None:
        msg = (
            f"invalid name {name!r}: names may only contain ASCII letters, "
            "digits, underscores and dashes, so they render as valid TOML keys"
        )
        raise ValueError(msg)


class ConfigurationError(ValueError):
    def __init__(self, path: str, message: str, /) -> None:
        self._path: str = path
        super().__init__(f"{path}: {message}" if path else message)

    @property
    def path(self) -> str:
        return self._path


def is_toml_value(value: object, /) -> bool:
    if type(value) is int:
        return TOML_INT_MIN <= value <= TOML_INT_MAX
    if type(value) in (str, float, bool, date, datetime):
        return True
    if type(value) is time:
        return value.tzinfo is None
    if type(value) is list:
        return all(is_toml_value(item) for item in value)
    if type(value) is dict:
        return all(
            type(key) is str and is_toml_value(item) for key, item in value.items()
        )
    return False
