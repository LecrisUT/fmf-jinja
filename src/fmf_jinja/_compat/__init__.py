"""
Compatibility modules.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterator
    from typing import Any


def walk(
    self: Path,
    top_down: bool = True,  # noqa: FBT001, FBT002
    on_error: Any = None,  # noqa: ANN401
    follow_symlinks: bool = False,  # noqa: FBT001, FBT002
) -> Iterator[tuple[Path, list[str], list[str]]]:
    if sys.version_info < (3, 12):
        import os

        for path_str, dirs, files in os.walk(
            self,
            topdown=top_down,
            onerror=on_error,
            followlinks=follow_symlinks,
        ):
            yield Path(path_str), dirs, files
    else:
        yield from self.walk(
            top_down=top_down,
            on_error=on_error,
            follow_symlinks=follow_symlinks,
        )


def relative_to(self: Path, other: Path, walk_up: bool = False) -> Path:  # noqa: FBT001, FBT002
    if sys.version_info < (3, 12):
        if not walk_up:
            return self.relative_to(other)
        self_parts = self.parts
        other_parts = other.parts
        anchor0, parts0 = self_parts[0], list(reversed(self_parts[1:]))
        anchor1, parts1 = other_parts[0], list(reversed(other_parts[1:]))
        if anchor0 != anchor1:
            msg = f"{self!r} and {other!r} have different anchors"
            raise ValueError(msg)
        while parts0 and parts1 and parts0[-1] == parts1[-1]:
            parts0.pop()
            parts1.pop()
        for part in parts1:
            if not part or part == ".":
                pass
            elif part == "..":
                msg = f"'..' segment in {other!r} cannot be walked"
                raise ValueError(msg)
            else:
                parts0.append("..")
        return Path(*reversed(parts0))
    return self.relative_to(other, walk_up=walk_up)
