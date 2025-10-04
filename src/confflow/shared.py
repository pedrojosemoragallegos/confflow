from __future__ import annotations

import typing
from datetime import date, datetime

YamlValue: typing.TypeAlias = (
    str
    | int
    | float
    | bool
    | datetime
    | date
    | bytes
    | list["YamlValue"]
    | dict[str, "YamlValue"]
)

YamlDict: typing.TypeAlias = dict[str, YamlValue]

yaml_indent: str = "  "


def create_frame(description: str) -> str:
    border: str = "+" + "-" * (len(description) + 2) + "+"
    content = f"| {description} |"

    return f"{border}\n{content}\n{border}"
