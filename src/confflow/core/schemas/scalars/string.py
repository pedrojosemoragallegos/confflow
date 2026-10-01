from __future__ import annotations

from confflow.core.definitions.string import String as StringDefinition

from .base import Scalar


class String(Scalar[str]):
    def __init__(
        self,
        name: str,
        description: str | None = None,
        /,
        *,
        optional: bool = False,
        default: str | None = None,
        minimum: int | None = None,
        maximum: int | None = None,
        length: int | None = None,
        pattern: str | None = None,
    ) -> None:
        super().__init__(
            name,
            description,
            optional=optional,
            definition=StringDefinition(
                minimum=minimum,
                maximum=maximum,
                length=length,
                pattern=pattern,
            ),
            default=default,
        )
