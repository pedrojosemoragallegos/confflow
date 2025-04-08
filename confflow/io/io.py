from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Type

from pydantic import BaseModel

from ..utils.types import PathLike, SchemaGroup
from .formatter import YAMLFormatter
from .formatter.base_formatter import BaseFormatter

OutputFormat = Literal["yaml"]

FORMATTER_MAP: Dict[OutputFormat, Type[BaseFormatter]] = {"yaml": YAMLFormatter}


def to_file(
    schemas: List[BaseModel],
    format: OutputFormat,
    path: PathLike,
    header: Optional[List[str]] = None,
    exclusive_groups: Optional[List[SchemaGroup]] = None,
    config_values: Optional[Dict[str, Dict[str, Any]]] = None,  # TODO typing
) -> None:
    path: Path = Path(path)

    formatter: Optional[Type[BaseFormatter]] = FORMATTER_MAP.get(format)
    if formatter is None:
        raise ValueError(f"Unsupported format: {format}")

    if not config_values:
        if exclusive_groups is None:
            exclusive_groups = []

    content: str = formatter.generate(
        schemas,
        header=header,
        exclusive_groups=exclusive_groups,
        config_values=config_values,
    )

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
