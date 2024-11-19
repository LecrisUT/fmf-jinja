"""Utility module."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import TYPE_CHECKING

from fmf import Tree

if TYPE_CHECKING:
    from collections.abc import Iterator
    from typing import TypeAlias

    WalkTuple: TypeAlias = tuple[Tree, list[str], list[str]]
    """Output of :py:meth:`fmf_tree_walk`"""


def _fmf_node_name(tree: Tree) -> str:
    """
    Equivalent of :py:attr:`pathlib.PurePath.name` for :py:class:`fmf.Tree`.

    :param tree: fmf tree
    :return: the path-like ``name`` attribute
    """
    if tree.parent is None:
        assert tree.name == "/"
        return "/"
    parent_name: str = tree.parent.name
    if not parent_name.endswith("/"):
        parent_name = f"{parent_name}/"
    assert parent_name in tree.name
    return tree.name.removeprefix(parent_name)


def get_fmf_files(tree: Tree, *, relative: bool = True) -> Iterator[Path]:
    """
    Get all fmf tree source files.

    :param tree: fmf tree
    :param relative: whether to output the source files relative to the root
    :return: all fmf source files including the ``.fmf`` folder files
    """

    def _return_path(path: Path) -> Path:
        if not relative:
            return path.absolute()
        return path.relative_to(tree_root)

    assert tree.parent is None
    tree_root = Path(tree.root)
    # First return the .fmf/version file
    # Including the `.fmf` folder itself so that it can be excluded
    yield _return_path(tree_root / ".fmf/version")
    # Next navigate the full fmf tree returning every source we find at most once
    sources_so_far = set()
    for curr_tree, _, _ in fmf_tree_walk(tree):
        for source in curr_tree.sources:
            if source in sources_so_far:
                continue
            sources_so_far.add(source)
            yield _return_path(Path(source))


def copy_fmf_tree(tree: Tree, output: Path) -> None:
    """
    Copy a fmf tree with all its sources.

    :param tree: fmf tree
    :param output: destination path
    """
    assert tree.parent is None
    tree_root = Path(tree.root)
    for source in get_fmf_files(tree):
        (output / source).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(tree_root / source, output / source)


def fmf_tree_walk(tree: Tree, *, top_down: bool = True) -> Iterator[WalkTuple]:
    """
    Equivalent of :py:meth:`pathlib.Path.walk` for :py:class:`fmf.Tree`.

    :param tree: fmf tree
    :param top_down: whether to output paths as it goes (from root ``/`` down to the
      leaves)
    :return: equivalent output of :py:meth:`pathlib.Path.walk`
    """
    # Based on the implementation from os.walk

    # Save the path list that need to be navigated
    # The navigation is always from top down, and depending on the top_down flag:
    # - top down: output the tuple as we go down
    # - bottom up: append to the navigation list until a leaf is reached and the
    #   results are popped in reverse order
    paths_or_output: list[Tree | WalkTuple] = [tree]
    while paths_or_output:
        curr_path = paths_or_output.pop()
        if isinstance(curr_path, tuple):
            # We are outputting from buttom up and reached a leaf
            # start yielding the results
            assert not top_down
            yield curr_path
            continue
        # Otherwise continue navigating
        assert isinstance(curr_path, Tree)

        # Construct the output
        branches: list[str] = []
        leaves: list[str] = []
        for child in curr_path.children.values():
            if child.children:
                branches.append(_fmf_node_name(child))
            else:
                leaves.append(_fmf_node_name(child))

        if top_down:
            # Output the result as we go
            yield curr_path, branches, leaves
        else:
            # Save the result for later
            paths_or_output.append((curr_path, branches, leaves))
        # Continue to navigate through the branches
        paths_or_output += [curr_path.children[branch] for branch in reversed(branches)]
