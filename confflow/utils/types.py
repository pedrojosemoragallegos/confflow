from collections import OrderedDict
from pathlib import Path
from typing import Any, Dict, List, Type, TypeAlias, Union

from pydantic import BaseModel

ParsedData: TypeAlias = Dict[
    str, Union[str, int, bool, List[Union[int, "ParsedData"]], "ParsedData", None]
]
NestedDict: TypeAlias = Dict[str, Union[Any, "NestedDict"]]
YAMLContent: TypeAlias = Dict[str, Any]
PathLike = Union[str, Path]

SchemaName: TypeAlias = str
SchemaMap: TypeAlias = OrderedDict[SchemaName, BaseModel]
SchemaGroup: TypeAlias = List[BaseModel]
ConfigType: TypeAlias = Type[BaseModel]
