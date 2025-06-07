from collections import OrderedDict
from collections.abc import ItemsView, Iterable, Iterator, KeysView
from typing import Optional, Tuple, TypeVar

from confflow.core.config.config_field_proxy import ConfigFieldProxy
from confflow.core.field.constraint.constraint import BaseConstraint
from confflow.core.field.field_factory import FieldFactory
from confflow.core.field.field_proxy import FieldProxy
from confflow.core.types import FieldType, FieldValue

T = TypeVar("T", bound=FieldValue)


class Config:
    def __init__(self, name: str, description: Optional[str] = None):
        self._name: str = name
        self._description: str = description or ""
        self._fields: OrderedDict[str, FieldType] = OrderedDict()
        self._defaults: list[Optional[FieldValue]] = list()
        self._requirets: list[bool] = list()

    def addField(
        self,
        value: T,
        *,
        name: str,
        description: Optional[str] = None,
        default_value: Optional[T] = None,
        required: bool = False,
        constraints: Optional[Iterable[BaseConstraint[T]]] = None,
    ) -> "Config":
        if name in self._fields:
            raise ValueError(f"Field with name '{name}' already exists.")

        self._fields[name] = FieldFactory(
            value=value, name=name, description=description, constraints=constraints
        )
        self._defaults.append(default_value)
        self._requirets.append(required)

        return self

    def keys(self) -> KeysView[str]:
        return self._fields.keys()

    def values(self) -> tuple[ConfigFieldProxy[FieldValue], ...]:
        return tuple(
            ConfigFieldProxy[FieldValue](
                field_proxy=FieldProxy(field=field),
                default_value=default_value,
                required=required,
            )
            for field, default_value, required in zip(
                self._fields.values(), self._defaults, self._requirets
            )
        )

    def items(self) -> ItemsView[str, ConfigFieldProxy[FieldValue]]:
        class ConfigItemsView(ItemsView[str, ConfigFieldProxy[FieldValue]]):
            def __init__(self, config: "Config"):
                self._config = config

            def __iter__(self) -> Iterator[Tuple[str, ConfigFieldProxy[FieldValue]]]:
                return (
                    (
                        key,
                        ConfigFieldProxy[FieldValue](
                            field_proxy=FieldProxy(field=field),
                            default_value=default,
                            required=required,
                        ),
                    )
                    for (key, field), default, required in zip(
                        self._config._fields.items(),
                        self._config._defaults,
                        self._config._requirets,
                    )
                )

            def __len__(self) -> int:
                return len(self._config._fields)

        return ConfigItemsView(self)

    def __getitem__(self, key: str) -> FieldValue:
        if key not in self._fields:
            raise KeyError(f"No field named '{key}'")
        index = list(self._fields.keys()).index(key)

        return ConfigFieldProxy[FieldValue](
            field_proxy=FieldProxy(field=self._fields[key]),
            default_value=self._defaults[index],
            required=self._requirets[index],
        ).value

    def __contains__(self, key: str) -> bool:
        return key in self._fields

    # TODO when iterating we should get the proxies since we need them to get the values like 'required' and 'default_value'
    def __iter__(
        self,
    ) -> Iterator[str]:
        return iter(self._fields)

    def __len__(self) -> int:
        return len(self._fields)

    # Only for iPython # TODO maybe remove here add as mixin or so
    def _ipython_key_completions_(self) -> list[str]:
        return list(self._fields.keys())
