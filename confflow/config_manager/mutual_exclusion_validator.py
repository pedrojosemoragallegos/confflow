import itertools
from typing import List, Type

from pydantic import BaseModel as BaseConfig


def is_mutual_exclusive(
    config_classes: List[Type[BaseConfig]],
    exclusive_groups: List[List[Type[BaseConfig]]],
):
    for group in exclusive_groups:
        group_classes: List[Type[BaseConfig]] = [
            config_class.__name__ for config_class in group
        ]
        active_classes: List[Type[BaseConfig]] = [
            config_class
            for config_class in config_classes
            if config_class in group_classes
        ]

        if len(active_classes) > 1:
            raise ValueError(
                f"Mutual exclusion conflict: {active_classes} are active in group {group_classes}."
            )


def validate_groups(groups: List[List[Type[BaseConfig]]]):
    flattened_groups: List[Type[BaseConfig]] = [
        item for group in groups for item in group
    ]

    if len(flattened_groups) != len(set(flattened_groups)):
        raise ValueError("Duplicate items found across mutually exclusive groups.")

    if has_conflicting_groups(groups):
        raise ValueError("Conflicting items found in mutually exclusive groups.")


def has_conflicting_groups(groups: List[List[Type[BaseConfig]]]) -> bool:
    for group1, group2 in itertools.combinations(groups, 2):
        if not set(group1).isdisjoint(group2):
            return True
    return False
