from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Mapping

    from confflow.core.fields import Field
    from confflow.core.schema import Schema
    from confflow.core.shared import TOMLValue

_MIN_TARGETS = 2


class Constraint(ABC):
    def __init__(self, *targets: Field[TOMLValue] | Schema) -> None:
        if len(targets) < _MIN_TARGETS:
            msg = "a constraint requires at least two targets"
            raise ValueError(msg)
        if len({id(target) for target in targets}) != len(targets):
            msg = "a constraint cannot repeat the same target"
            raise ValueError(msg)
        self._targets = targets

    @property
    def targets(self) -> tuple[Field[TOMLValue] | Schema, ...]:
        return self._targets

    @abstractmethod
    def check(
        self,
        values: Mapping[str, TOMLValue],
        present: frozenset[str],
        path: str,
        /,
    ) -> None: ...

    @abstractmethod
    def describe(self) -> str: ...
