from __future__ import annotations

from typing import TYPE_CHECKING, get_args, get_origin

from confflow.core.definitions.base import Definition

if TYPE_CHECKING:
    from confflow.core.types import Value


def get_definition_value_type(definition: Definition[Value], /) -> type[Value]:
    for definition_class in type(definition).__mro__:
        for base in definition_class.__dict__.get("__orig_bases__", ()):
            if get_origin(base) is Definition:
                (value_type,) = get_args(base)
                if isinstance(value_type, type):
                    return value_type
    raise TypeError(
        f"could not determine value type for {type(definition).__qualname__}"
    )
