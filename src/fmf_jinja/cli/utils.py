from contextlib import contextmanager
from pathlib import Path
from os import getcwd, chdir

from typing import Union, Iterator


@contextmanager
def cd(target: Union[str, Path]) -> Iterator[None]:
    """
    Manage cd in a pushd/popd fashion.

    Usage:

        with cd(tmpdir):
          do something in tmpdir
    """
    curdir = getcwd()
    chdir(target)
    try:
        yield
    finally:
        chdir(curdir)
