from __future__ import annotations

from tomllib import load
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


def parse(path: Path) -> object:
    with path.open("rb") as file:
        return load(file)
