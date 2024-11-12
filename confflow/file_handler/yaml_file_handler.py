from pathlib import Path

import yaml

from confflow.types import ParsedData, PathLike

from .file_handler import FileHandler


class YAMLFileHandler(FileHandler):
    @staticmethod
    def load(input_path: PathLike) -> ParsedData:
        input_path: Path = Path(input_path)
        with input_path.open("r") as input_file:
            yaml_content: ParsedData = yaml.safe_load(input_file)

        return yaml_content
