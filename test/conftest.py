from __future__ import annotations

import difflib
import filecmp
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from fmf import Tree

if TYPE_CHECKING:
    from _pytest.fixtures import SubRequest

DIR = Path(__file__).parent.resolve()
BASE = DIR.parent


class dircmp(filecmp.dircmp[str]):  # noqa: N801
    """
    Compare the content of dir1 and dir2.

    In contrast with filecmp.dircmp, this
    subclass compares the content of files with the same path.
    """

    def phase3(self):
        """Find out differences between common files.
        Ensure we are using content comparison with shallow=False.
        """
        fcomp = filecmp.cmpfiles(
            self.left,
            self.right,
            self.common_files,
            shallow=False,
        )
        self.same_files, self.diff_files, self.funny_files = fcomp


def get_diff(
    left: Path,
    right: Path,
    root_left: Path | None = None,
    root_right: Path | None = None,
) -> tuple[list[Path], list[Path], list[Path], list[Path]]:
    root_left = root_left or left
    root_right = root_right or right
    compared = dircmp(left, right)
    left_only = [(left / f).relative_to(root_left) for f in compared.left_only]
    right_only = [(right / f).relative_to(root_right) for f in compared.right_only]
    diff_files = [(left / f).relative_to(root_left) for f in compared.diff_files]
    funny_files = [(left / f).relative_to(root_left) for f in compared.funny_files]
    # Accumulate differences recursively
    for subdir in compared.common_dirs:
        sub_compared = get_diff(left / subdir, right / subdir, root_left, root_right)
        left_only += [(left / f).relative_to(root_left) for f in sub_compared[0]]
        right_only += [(right / f).relative_to(root_right) for f in sub_compared[1]]
        diff_files += [(left / f).relative_to(root_left) for f in sub_compared[2]]
        funny_files += [(left / f).relative_to(root_left) for f in sub_compared[3]]
    return left_only, right_only, diff_files, funny_files


def is_same(dir1: Path, dir2: Path) -> bool:
    """
    Compare two directory trees content.

    Return False if they differ, True is they are the same.
    """
    compared = dircmp(dir1, dir2)
    if (
        compared.left_only
        or compared.right_only
        or compared.diff_files
        or compared.funny_files
    ):
        return False
    return all(is_same(dir1 / subdir, dir2 / subdir) for subdir in compared.common_dirs)


@dataclass
class PathComp:
    path: Path

    def __eq__(self, other):
        if isinstance(other, PathComp):
            return is_same(self.path, other.path)
        if isinstance(other, Path):
            return is_same(self.path, other)
        return False


def pytest_assertrepr_compare(config, op, left, right):
    if not isinstance(left, PathComp) or not isinstance(right, PathComp):
        return None
    if op != "==":
        return None
    output = [
        "Compared path contents:",
        f"'{left.path}' != '{right.path}'",
    ]
    if config.getoption("verbose") < 1:
        return output
    left_only, right_only, diff_files, funny_files = get_diff(left.path, right.path)
    if left_only:
        output += ["Left only:"]
        output += [f"< {fil}" for fil in left_only]
    if right_only:
        output += ["Right only:"]
        output += [f"> {fil}" for fil in right_only]
    if diff_files:
        output += ["Diff files:"]
        for fil in diff_files:
            output += [f"!  {fil}"]
            if config.getoption("verbose") > 1:
                left_f = left.path / fil
                right_f = right.path / fil
                with left_f.open("r") as f:
                    left_lines = f.readlines()
                with right_f.open("r") as f:
                    right_lines = f.readlines()
                comp_file = difflib.unified_diff(
                    left_lines,
                    right_lines,
                    fromfile=str(left_f),
                    tofile=str(right_f),
                )
                output += comp_file
    if funny_files:
        output += ["Funny files (couldn't compare):"]
        output += [f"? {fil}" for fil in funny_files]
    return output


@dataclass
class TreeFixture:
    tree: Tree
    out_path: PathComp
    expected_path: PathComp


@pytest.fixture()
def fmf_tree(tmp_path: Path, request: SubRequest) -> TreeFixture:
    path = Path(request.param)
    tree_path = DIR / "data/input" / path
    expected_path = DIR / "data/output" / path
    tree = Tree(tree_path)
    return TreeFixture(tree, PathComp(tmp_path), PathComp(expected_path))


def set_test_type_marker(
    config: pytest.Config,
    items: list[pytest.Item],
    test_type: str,
) -> None:
    rootdir = config.rootpath
    test_path = rootdir / "test" / test_type
    for item in items:
        if not item.path.is_relative_to(test_path):
            continue
        item.add_marker(test_type)


def pytest_collection_modifyitems(
    session: pytest.Session,  # noqa: ARG001
    config: pytest.Config,
    items: list[pytest.Item],
) -> None:
    set_test_type_marker(config, items, "smoke")
    set_test_type_marker(config, items, "functional")
