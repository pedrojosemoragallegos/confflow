from os import PathLike
from pathlib import Path
from typing import Literal

from confflow.file_handler.factory import file_hanlder_factory


def save_configuration(
    type: Literal["yaml"],
    output_path: PathLike,
    data: str,
):
    output_path: Path = Path(output_path)
    file_hanlder_factory(type).save(output_path, data)
