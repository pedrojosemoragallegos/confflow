from types import MappingProxyType

from confflow.types import Value, View


def freeze(
    obj: Value,
) -> View:
    if isinstance(obj, dict):
        return MappingProxyType(obj)  # type: ignore
    elif isinstance(obj, list):
        return tuple(obj)  # type: ignore
    elif isinstance(obj, set):
        return frozenset(obj)  # type: ignore
    elif isinstance(obj, str):
        return obj
    elif isinstance(obj, bool):
        return obj
    else:
        raise ValueError("Not supported value.")
