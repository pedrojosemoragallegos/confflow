from __future__ import annotations

from typing import final

from .validation_error import ValidationError


@final
class InvalidValueError(ValidationError):
    __slots__ = ()
