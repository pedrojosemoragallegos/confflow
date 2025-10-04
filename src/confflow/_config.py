from dataclasses import make_dataclass
from typing import Any, Protocol, TypeVar, cast

from ._shared import YamlValue


class Config(Protocol):
    def __getitem__(self, key: str) -> YamlValue: ...
    def __setitem__(self, key: str, value: YamlValue) -> None: ...


T = TypeVar("T", bound=Config)


def dict_to_dataclass(
    name: str,
    data: dict[str, Any],
    *,
    frozen: bool = False,
) -> Config:
    fields: list[tuple[str, type[Any], Any]] = []
    processed_data: dict[str, Any] = {}

    for k, v in data.items():
        if isinstance(v, dict):
            nested_class = dict_to_dataclass(
                f"{name}_{k.capitalize()}",
                v,  # type: ignore  # noqa: PGH003
                frozen=frozen,
            )
            fields.append((k, type(nested_class), nested_class))
            processed_data[k] = nested_class
        elif isinstance(v, list) and v and isinstance(v[0], dict):
            nested_items = [
                dict_to_dataclass(
                    f"{name}_{k.capitalize()}Item",
                    item,  # type: ignore  # noqa: PGH003
                    frozen=frozen,
                )
                for item in v  # type: ignore  # noqa: PGH003
            ]
            fields.append((k, list[Any], nested_items))
            processed_data[k] = nested_items
        else:
            fields.append((k, type(v), v))  # type: ignore  # noqa: PGH003
            processed_data[k] = v

    def __getitem__(self: str, key: str) -> YamlValue | Config:  # noqa: N807
        return getattr(self, key)

    def __setitem__(self: str, key: str, value: YamlValue) -> None:  # noqa: N807
        setattr(self, key, value)

    field_definitions: list[tuple[str, type[Any]]] = [
        (field_name, field_type) for field_name, field_type, _ in fields
    ]

    cls = make_dataclass(
        name,
        field_definitions,
        frozen=frozen,
        namespace={"__getitem__": __getitem__, "__setitem__": __setitem__},
    )
    return cast("Config", cls(**processed_data))
