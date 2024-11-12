from pathlib import Path
from typing import Any, Dict, List, TypeAlias, Union

ParsedData: TypeAlias = Dict[
    str, Union[str, int, bool, List[Union[int, "ParsedData"]], "ParsedData", None]
]
NestedDict: TypeAlias = Dict[str, Union[Any, "NestedDict"]]
YAMLContent: TypeAlias = Dict[str, Any]
PathLike = Union[str, Path]
