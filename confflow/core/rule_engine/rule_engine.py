from .._rules import BaseRule
from .conflict_checker import check_conflicts


class RuleEngine:
    def __init__(self):
        self._rules: list[BaseRule] = []

    def add_rule(self, rule: BaseRule) -> None:
        check_conflicts(self._rules + [rule])
        self._rules.append(rule)

    def validate_selection(self, selection: set[str]) -> bool:
        return all(rule.validate(selection) for rule in self._rules)
