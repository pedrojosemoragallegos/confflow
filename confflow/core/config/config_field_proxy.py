from types import MappingProxyType
from typing import Generic, TypeVar

from ..field.field_proxy import FieldProxy
from ..types import FieldValue

T = TypeVar("T", bound=FieldValue)


class ConfigFieldProxy(Generic[T]):
    def __init__(
        self, field_proxy: FieldProxy[T], default_value: T, required: bool = False
    ):
        self._field_proxy = field_proxy
        self._default_value = default_value
        self._required = required

    @property
    def name(self) -> str:
        return self._field_proxy.name

    @property
    def description(self) -> str:
        return self._field_proxy.description

    @property
    def value(self) -> T:
        return self._field_proxy.value

    @property
    def default_value(self) -> T:
        default_value: T = self._default_value

        if isinstance(default_value, dict):
            return MappingProxyType(default_value)
        elif isinstance(default_value, list):
            return tuple(default_value)
        elif isinstance(default_value, set):
            return frozenset(default_value)
        else:
            return default_value  # primitives or already immutable

    @property
    def required(self) -> bool:
        return self._required
