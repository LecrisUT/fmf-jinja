from fmf import Tree as FMFTree
from pathlib import Path

from typing import Any


class Tree(FMFTree):
    def __init__(self, path: Path, **kwargs: Any) -> None:
        super().__init__(str(path), **kwargs)
