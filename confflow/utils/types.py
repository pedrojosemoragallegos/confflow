from collections import OrderedDict
from pathlib import Path
from typing import Any, Dict, List, Type, TypeAlias, Union

from pydantic import BaseModel as BaseConfig

ParsedData: TypeAlias = Dict[
    str, Union[str, int, bool, List[Union[int, "ParsedData"]], "ParsedData", None]
]
NestedDict: TypeAlias = Dict[str, Union[Any, "NestedDict"]]
YAMLContent: TypeAlias = Dict[str, Any]
PathLike = Union[str, Path]

ConfigName: TypeAlias = str
SchemaMap: TypeAlias = OrderedDict[ConfigName, BaseConfig]
ConfigGroup: TypeAlias = List[BaseConfig]
ConfigType: TypeAlias = Type[BaseConfig]
