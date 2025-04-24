from ...common.types import Schema
from .._rules import BaseRule
from .conflict_checker import check_conflicts


class RuleEngine:
    def __init__(self):
        self._rules: set[BaseRule] = set()

    def add_rules(self, *rules: BaseRule) -> None:
        check_conflicts(self._rules.union(set(rules)))

        self._rules.update(rules)

    def add_rule(self, rule: BaseRule) -> None:
        self.add_rules(rule)

    def validate_selection(self, *schema: Schema) -> bool:
        return all(rule.validate(*schema) for rule in self._rules)
