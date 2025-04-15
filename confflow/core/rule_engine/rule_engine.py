from ...common.types import BaseModel, Schema
from ..registry.schema_registry import SchemaRegistry
from .base_rule import BaseRule


class RuleEngine:
    def __init__(self, registry: SchemaRegistry):
        self._rules: list[BaseRule] = []
        self._registry: SchemaRegistry = registry

    def _is_schema_registered(self, rule: BaseRule) -> bool:
        return rule.referenced_schemas.issubset(self._registry.schema_types)

    def _is_rule_already_registered(self, rule: BaseRule) -> bool:
        return rule in self._rules

    def register(self, rule: BaseRule):
        if not self._is_schema_registered(rule):
            invalid_schemas: set[Schema] = rule.referenced_schemas - set(
                self._registry.schema_types
            )

            raise ValueError(f"Schemas in rule are not registered: {invalid_schemas}")

        if self._is_rule_already_registered(rule):
            raise ValueError("Rule is already registered.")

        self._rules.append(rule)

    def validate(self, active_configs: list[BaseModel]):
        active_schemas: list[Schema] = [config.__class__ for config in active_configs]

        for rule in self._rules:
            if rule.is_violated(active_schemas):
                raise Exception(f"Rule violated: {rule}")
