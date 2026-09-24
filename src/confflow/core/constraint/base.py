from __future__ import annotations

from typing import TYPE_CHECKING

from typing_extensions import override

from confflow.core.shared import ConfigurationError

from .constraint import Constraint

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping

    from confflow.core.fields import Field
    from confflow.core.schema import Schema
    from confflow.core.shared import TOMLValue


class _Constraint(Constraint):
    def __init__(
        self,
        name: str,
        targets: tuple[Field[TOMLValue] | Schema, ...],
        check: Callable[[Mapping[str, TOMLValue], frozenset[str]], bool],
        /,
    ) -> None:
        super().__init__(*targets)
        self._name = name
        self._check = check

    @property
    def name(self) -> str:
        return self._name

    @override
    def check(
        self,
        values: Mapping[str, TOMLValue],
        present: frozenset[str],
        path: str,
        /,
    ) -> None:
        try:
            valid = self._check(values, present)
        except (TypeError, ValueError, KeyError) as exc:
            raise ConfigurationError(path, f"{self.describe()}: {exc}") from exc
        if not valid:
            raise ConfigurationError(path, self.describe())

    @override
    def describe(self) -> str:
        return f"{self.name}({', '.join(target.name for target in self.targets)})"
