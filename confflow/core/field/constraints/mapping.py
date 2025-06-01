from confflow.protocols import Constraint
from confflow.types import StructuredValues


class HasKeys(Constraint[dict[str, StructuredValues]]):
    def __init__(self, keys: list[str]) -> None:
        self._required_keys = set(keys)

    def __call__(self, value: dict[str, StructuredValues]) -> None:
        missing = self._required_keys - value.keys()
        if missing:
            raise ValueError(f"dict is missing keys: {missing}")


class HasNoKeys(Constraint[dict[str, StructuredValues]]):
    def __init__(self, keys: list[str]) -> None:
        self._forbidden_keys = set(keys)

    def __call__(self, value: dict[str, StructuredValues]) -> None:
        found = self._forbidden_keys & value.keys()
        if found:
            raise ValueError(f"dict must not contain keys: {found}")


class HasKeyValue(Constraint[dict[str, StructuredValues]]):
    def __init__(self, key: str, expected_value: StructuredValues) -> None:
        self.key = key
        self.expected_value = expected_value

    def __call__(self, value: dict[str, StructuredValues]) -> None:
        if self.key not in value:
            raise ValueError(f"Missing required key: {self.key}")
        if value[self.key] != self.expected_value:
            raise ValueError(
                f"Key {self.key} must have value {self.expected_value}, found {value[self.key]}"
            )


class KeyConstraint(Constraint[dict[str, StructuredValues]]):
    def __init__(self, key_constraint: Constraint[str]) -> None:
        self.key_constraint = key_constraint

    def __call__(self, value: dict[str, StructuredValues]) -> None:
        for key in value:
            try:
                self.key_constraint(key)
            except ValueError as e:
                raise ValueError(f"Key {key} violates constraint: {e}") from e


class ValueConstraint(Constraint[dict[str, StructuredValues]]):
    def __init__(self, value_constraint: Constraint[StructuredValues]) -> None:
        self.value_constraint = value_constraint

    def __call__(self, value: dict[str, StructuredValues]) -> None:
        for k, v in value.items():
            try:
                self.value_constraint(StructuredValues)
            except ValueError as e:
                raise ValueError(f"Value at key {k} violates constraint: {e}") from e


class ItemConstraint(Constraint[dict[str, StructuredValues]]):
    def __init__(
        self, item_constraint: Constraint[tuple[str, StructuredValues]]
    ) -> None:
        self.item_constraint = item_constraint

    def __call__(self, value: dict[str, StructuredValues]) -> None:
        for item in value.items():
            try:
                self.item_constraint(item)
            except ValueError as e:
                raise ValueError(f"Item {item} violates constraint: {e}") from e
