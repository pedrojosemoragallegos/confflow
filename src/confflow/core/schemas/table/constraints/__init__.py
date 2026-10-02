"""Relational constraints between direct children of one Table.

Operands are child names, never schema objects or paths. Presence means key
membership, not truthiness: False, zero and empty values are still present.
Config composes schemas but does not accept relational constraints.
"""

from .at_least_one_of import AtLeastOneOf
from .at_most_one_of import AtMostOneOf
from .base import Constraint
from .comparision import (
    Comparision,
    GreaterThan,
    GreaterThanOrEqual,
    LessThan,
    LessThanOrEqual,
)
from .equal import Equal
from .exactly_one_of import ExactlyOneOf
from .forbids import Forbids
from .not_equal import NotEqual
from .required_together import RequiredTogether
from .requires import Requires

__all__: list[str] = [
    "AtLeastOneOf",
    "AtMostOneOf",
    "Comparision",
    "Constraint",
    "Equal",
    "ExactlyOneOf",
    "Forbids",
    "GreaterThan",
    "GreaterThanOrEqual",
    "LessThan",
    "LessThanOrEqual",
    "NotEqual",
    "RequiredTogether",
    "Requires",
]
