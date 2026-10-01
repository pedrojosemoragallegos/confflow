from __future__ import annotations

from typing import final

from ..definitions.exceptions import DefinitionError


@final
class InvalidValueError(DefinitionError):
    __slots__ = ()
