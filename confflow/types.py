from datetime import datetime
from typing import TypeAlias, Union

# sadly pythons typing system doesn't allow better typing to avoid redundancy
Scalar: TypeAlias = Union[str, int, float, bool, datetime, bytes]
ScalarList: TypeAlias = Union[
    list[str], list[int], list[float], list[bool], list[datetime], list[bytes]
]

Value: TypeAlias = Union[Scalar, ScalarList]
