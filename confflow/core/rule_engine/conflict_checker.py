from typing import Callable, NamedTuple, Optional, Type, get_origin

from .rules import (
    AllOrNone,
    BaseRule,
    ExactlyN,
    MutuallyExclusive,
    OneOfGroup,
    RequiresOneOf,
)


class ConflictRule(NamedTuple):
    cls_1: Type[BaseRule]
    cls_1_label: str
    cls_2: Type[BaseRule]
    cls_2_label: str
    condition: Optional[Callable[..., bool]] = None


CONFLICT_RULES: list[ConflictRule] = [
    ConflictRule(
        cls_1=MutuallyExclusive,
        cls_1_label="Mutually Exclusive",
        cls_2=AllOrNone,
        cls_2_label="All-Or-None",
    ),
    ConflictRule(
        cls_1=MutuallyExclusive,
        cls_1_label="Mutually Exclusive",
        cls_2=OneOfGroup,
        cls_2_label="One-Of-Group",
    ),
    ConflictRule(
        cls_1=MutuallyExclusive,
        cls_1_label="Mutually Exclusive",
        cls_2=RequiresOneOf,
        cls_2_label="Requires-One-Of",
    ),
    ConflictRule(
        cls_1=MutuallyExclusive,
        cls_1_label="Mutually Exclusive",
        cls_2=ExactlyN,
        cls_2_label="Exactly-N",
        condition=lambda n: n > 1,
    ),
    ConflictRule(
        cls_1=AllOrNone,
        cls_1_label="All-Or-None",
        cls_2=OneOfGroup,
        cls_2_label="One-Of-Group",
    ),
    ConflictRule(
        cls_1=AllOrNone,
        cls_1_label="All-Or-None",
        cls_2=ExactlyN,
        cls_2_label="Exactly-N",
        condition=lambda n, size: n not in (0, size),
    ),
    ConflictRule(
        cls_1=OneOfGroup,
        cls_1_label="One-Of-Group",
        cls_2=RequiresOneOf,
        cls_2_label="Requires-One-Of",
    ),
    ConflictRule(
        cls_1=OneOfGroup,
        cls_1_label="One-Of-Group",
        cls_2=ExactlyN,
        cls_2_label="Exactly-N",
        condition=lambda n: n != 1,
    ),
    ConflictRule(
        cls_1=RequiresOneOf,
        cls_1_label="Requires-One-Of",
        cls_2=ExactlyN,
        cls_2_label="Exactly-N",
        condition=lambda n: n < 2,
    ),
]


def check_conflicts(
    rules: list[BaseRule], conflict_rules: list[ConflictRule] = CONFLICT_RULES
) -> None:
    for i, rule_a in enumerate(rules):
        for rule_b in rules[i + 1 :]:
            _check_pair(rule_a, rule_b, conflict_rules)


def _check_pair(
    rule_a: BaseRule, rule_b: BaseRule, conflict_rules: list[ConflictRule]
) -> None:
    if not (rule_a.items & rule_b.items):
        return

    for rule in conflict_rules:
        if _match_pair(
            rule_a=rule_a, rule_b=rule_b, cls_1=rule.cls_1, cls_2=rule.cls_2
        ):
            n: Optional[int] = getattr(rule_a, "_n", None) or getattr(
                rule_b, "_n", None
            )

            if rule.condition is None:
                raise ValueError(
                    f"Conflict between '{rule.cls_1_label}' and '{rule.cls_2_label}'"
                )

            if {rule.cls_1, rule.cls_2} == {AllOrNone, ExactlyN}:
                items = rule_a.items if isinstance(rule_a, AllOrNone) else rule_b.items
                if rule.condition(n, len(items)):
                    raise ValueError(
                        f"Conflict between '{rule.cls_1_label}' and '{rule.cls_2_label}' (n={n}, size={len(items)})"
                    )
            elif rule.condition(n):
                raise ValueError(
                    f"Conflict between '{rule.cls_1_label}' and '{rule.cls_2_label}' (n={n})"
                )


def _match_pair(
    rule_a: BaseRule,
    rule_b: BaseRule,
    cls_1: Type[BaseRule],
    cls_2: Type[BaseRule],
) -> bool:
    return (
        isinstance(rule_a, get_origin(cls_1)) and isinstance(rule_b, get_origin(cls_2))
    ) or (
        isinstance(rule_a, get_origin(cls_2)) and isinstance(rule_b, get_origin(cls_1))
    )
