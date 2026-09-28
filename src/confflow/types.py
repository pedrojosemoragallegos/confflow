from __future__ import annotations

from collections.abc import Mapping
from datetime import date, datetime, time
from typing import TypeAlias

_ConfigurationScalar: TypeAlias = str | int | float | bool | datetime | date | time
ConfigurationValue: TypeAlias = (
    _ConfigurationScalar
    | tuple["ConfigurationValue", ...]
    | frozenset[_ConfigurationScalar]
    | Mapping[str, "ConfigurationValue"]
)
ConfigurationData: TypeAlias = Mapping[str, ConfigurationValue]

__all__ = ("ConfigurationData", "ConfigurationValue")
