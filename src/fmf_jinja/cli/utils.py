"""Various helper constructs."""

from __future__ import annotations

import os
from contextlib import contextmanager
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterator


@contextmanager
def cd(target: str | Path) -> Iterator[None]:
    """
    Manage cd in a pushd/popd fashion.

    Usage:

        with cd(tmpdir):
          do something in tmpdir
    """
    curdir = Path.cwd()
    os.chdir(target)
    try:
        yield
    finally:
        os.chdir(curdir)
