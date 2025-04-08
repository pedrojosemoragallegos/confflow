from typing import Literal

from .file_handler import FileHandler
from .yaml_file_handler import YAMLFileHandler


def file_hanlder_factory(type: Literal["yaml"]) -> FileHandler:
    if type == "yaml":
        return YAMLFileHandler
    else:
        raise ValueError(f"Unsupported type: {type}. Allowed types are: 'yaml'.")
