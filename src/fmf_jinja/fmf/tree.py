"""Module defining :py:class:`Tree`."""

from __future__ import annotations

from typing import TYPE_CHECKING

from fmf import Tree as FMFTree

if TYPE_CHECKING:
    from pathlib import Path


class Tree(FMFTree):
    """Wrapper of the :py:class:`fmf.Tree`."""

    def __init__(self, path: Path, **kwargs) -> None:  # type: ignore[no-untyped-def]  # noqa: D107, ANN003
        super().__init__(str(path), **kwargs)
