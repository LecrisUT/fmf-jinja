import pytest
import filecmp
from difflib import unified_diff
from pathlib import Path
from dataclasses import dataclass

from _pytest.fixtures import SubRequest
from typing import Optional

from fmf_jinja.fmf import Tree

DIR = Path(__file__).parent.resolve()
BASE = DIR.parent


# noinspection PyPep8Naming
class dircmp(filecmp.dircmp[str]):
    """
    Compare the content of dir1 and dir2. In contrast with filecmp.dircmp, this
    subclass compares the content of files with the same path.
    """

    def phase3(self):
        """
        Find out differences between common files.
        Ensure we are using content comparison with shallow=False.
        """
        fcomp = filecmp.cmpfiles(
            self.left, self.right, self.common_files, shallow=False
        )
        self.same_files, self.diff_files, self.funny_files = fcomp


def get_diff(
    left: Path,
    right: Path,
    root_left: Optional[Path] = None,
    root_right: Optional[Path] = None,
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
    for subdir in compared.common_dirs:
        if not is_same(dir1 / subdir, dir2 / subdir):
            return False
    return True


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
    if isinstance(left, PathComp) and isinstance(right, PathComp) and op == "==":
        output = [
            f"Compared path contents:",
            f"'{left.path}' != '{right.path}'",
        ]
        if config.getoption("verbose") < 1:
            return output
        left_only, right_only, diff_files, funny_files = get_diff(left.path, right.path)
        if left_only:
            output.append("Left only:")
            for f in left_only:
                output.append(f"<  {f}")
        if right_only:
            output.append("Right only:")
            for f in right_only:
                output.append(f">  {f}")
        if diff_files:
            output.append("Diff files:")
            for f in diff_files:
                output.append(f"!  {f}")
                if config.getoption("verbose") > 1:
                    left_f = left.path / f
                    right_f = right.path / f
                    with left_f.open("r") as fil:
                        left_lines = fil.readlines()
                    with right_f.open("r") as fil:
                        right_lines = fil.readlines()
                    comp_file = unified_diff(
                        left_lines,
                        right_lines,
                        fromfile=str(left_f),
                        tofile=str(right_f),
                    )
                    output += comp_file
        if funny_files:
            output.append("Funny files (couldn't compare):")
            for f in funny_files:
                output.append(f"?  {f}")
        return output


@dataclass
class TreeFixture:
    tree: Tree
    out_path: PathComp
    expected_path: PathComp


@pytest.fixture
def fmf_tree(tmp_path: Path, request: SubRequest) -> TreeFixture:
    path = Path(request.param)
    tree_path = DIR / "data" / "input" / "trees" / path
    expected_path = DIR / "data" / "output" / "trees" / path
    assert tree_path.exists() and tree_path.is_dir()
    assert tree_path.joinpath(".fmf", "version").exists()
    assert expected_path.exists() and expected_path.is_dir()
    tree = Tree(tree_path)
    return TreeFixture(tree, PathComp(tmp_path), PathComp(expected_path))
