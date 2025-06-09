from datetime import datetime
from typing import TypeAlias, Union

DictValue: TypeAlias = dict[str, Union[str, int, float, bool, datetime, bytes]]
ListValue: TypeAlias = list[Union[str, int, float, bool, datetime, bytes]]
SetValue: TypeAlias = set[Union[str, int, float, bool, datetime, bytes]]

Value: TypeAlias = Union[
    str,
    int,
    float,
    bool,
    datetime,
    bytes,
    dict[str, Union[str, int, float, bool, datetime, bytes]],
    list[Union[str, int, float, bool, datetime, bytes]],
    set[Union[str, int, float, bool, datetime, bytes]],
]
