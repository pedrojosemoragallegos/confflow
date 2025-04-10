from pathlib import Path
from typing import Any, Dict, List, Type, TypeAlias, Union

from pydantic import BaseModel

ParsedData: TypeAlias = Dict[
    str, Union[str, int, bool, List[Union[int, "ParsedData"]], "ParsedData", None]
]

NestedDict: TypeAlias = Dict[str, Union[Any, "NestedDict"]]
YAMLContent: TypeAlias = Dict[str, Any]
PathLike = Union[str, Path]

Schema: TypeAlias = Type[BaseModel]
SchemaName: TypeAlias = str
SchemaDescription: TypeAlias = str
SchemaGroup: TypeAlias = List[Schema]
SchemaInstance: TypeAlias = BaseModel
