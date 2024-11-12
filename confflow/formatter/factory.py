from typing import Literal

from .formatter import Formatter
from .yaml_formatter import YAMLFormatter


def formatter_factory(type: Literal["yaml"]) -> Formatter:
    if type == "yaml":
        return YAMLFormatter
    else:
        raise ValueError(f"Unsupported type: {type}. Allowed types are: 'yaml'.")
