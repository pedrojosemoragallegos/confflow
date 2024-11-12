from abc import ABC, abstractmethod
from pathlib import Path

from confflow.types import ParsedData, PathLike


class FileHandler(ABC):
    @staticmethod
    @abstractmethod
    def load(input_path: PathLike) -> ParsedData: ...

    @staticmethod
    @abstractmethod
    def save(
        output_path: PathLike,
        data: str,
    ):
        output_path: Path = Path(output_path)
        with output_path.open("w") as output_file:
            output_file.write(data)
