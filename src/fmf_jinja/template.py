"""Module for the Template fmf data type."""

from __future__ import annotations

import functools
import shutil
import tempfile
from pathlib import Path

import attrs
from fmf import Tree
from jinja2 import Environment

from .generators import FullGenerator
from .utils import copy_fmf_tree, fmf_tree_walk, get_fmf_files

DEFAULT_JINJA_ENV = Environment(
    keep_trailing_newline=True,
    trim_blocks=True,
    autoescape=True,
)
"""Default settings for the jinja environment."""


@attrs.define
class TemplateContext:
    """
    Generator's run context.
    """

    tree_root: Tree
    """Full fmf tree being processed."""
    jinja_env: Environment = attrs.field(init=False, default=DEFAULT_JINJA_ENV)
    """The base jinja environment."""
    previous_ctx: TemplateContext | None = None
    """The context of the previous run."""
    recursive: bool = True
    """Whether to recursively generate the templated files."""
    generated_fmf: bool = attrs.field(init=False, default=False)
    """Whether a fmf file was generated in the current run."""
    _tmp_path: Path = attrs.field(init=False, default=None)
    """See :py:attr:`tmp_path`."""
    _curr_path: str | None = attrs.field(init=False, default=None)
    """See :py:attr:`curr_path`."""

    def __enter__(self) -> FullGenerator:  # noqa: D105
        assert self._curr_path is not None
        assert self.tmp_path.exists()
        return FullGenerator(self)

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:  # noqa: D105, ANN001
        self._curr_path = None

    @property
    def curr_path(self) -> str:
        """Current path string that is being processed."""
        if self._curr_path is None:
            msg = "Context is used without __enter__"
            raise RuntimeError(msg)
        return self._curr_path

    @property
    def tmp_path(self) -> Path:
        """Temporary path where the current run's output is placed."""
        if self._tmp_path is None:
            msg = "Temporary folder of Context was not created"
            raise RuntimeError(msg)
        return self._tmp_path

    @property
    def output_path(self) -> Path:
        """Output path of the current node being processed."""
        return self.tmp_path / self.curr_path

    @property
    def tree(self) -> Tree:
        """Current fmf tree node."""
        # TODO: fmf fails if node has no children but we are trying to navigate self
        if not self.tree_root.children:
            assert self.curr_path == "."
            return self.tree_root
        path_parts = self.curr_path.removeprefix(".").split("/")
        tree = self.tree_root
        for part in path_parts:
            tree = tree[f"/{part}"]
        return tree

    @property
    def tree_path(self) -> Path:
        """Path to the current tree node."""
        return self.tree_root_path / self.curr_path

    @functools.cached_property
    def tree_root_path(self) -> Path:
        """Path to the tree root directory."""
        return Path(self.tree_root.root)

    @functools.cached_property
    def fmf_files(self) -> set[Path]:
        """Fmf source files (cache)."""
        return set(get_fmf_files(self.tree_root))

    def join_path(self, path: Path, output_root: Path | None = None) -> Path:
        """
        Join a path to the current tree context.

        If the path is absolute, it navigates from the tree root or output_root,
        otherwise it navigates from the current node's path.

        :param path: path object to join
        :param output_root: root path where to construct the path.
          Defaults to `tree_root_path`
        :return: joined path
        """
        if not output_root:
            output_root = self.tree_root_path
        if path.is_absolute():
            return output_root / str(path).removeprefix("/")
        return output_root / self.curr_path / path

    def generate(self, output: Path) -> None:
        """
        Generate the templated files from the tree's data.

        :param output: output path where the rendered fmf tree is placed
        """
        with tempfile.TemporaryDirectory(prefix="fmf-jinja-") as tmp_path:
            self._tmp_path = Path(tmp_path)
            copy_fmf_tree(self.tree_root, self.tmp_path)
            # If tree has a single node then we cannot use leaves from walk
            if not self.tree_root.children:
                self._curr_path = "."
                with self as generator:
                    generator.generate()
            else:
                # Walk through the tree and generate the template for each leaf
                for curr_tree, _, leaves in fmf_tree_walk(self.tree_root):
                    for leaf in leaves:
                        # Construct the full leaf path, dropping the initial `/`
                        full_leaf_path = str(Path(curr_tree.name) / leaf)
                        full_leaf_path = full_leaf_path.removeprefix("/")
                        self._curr_path = full_leaf_path
                        with self as generator:
                            generator.generate()
            # Check if we need to run the generator again
            if self.recursive and self.generated_fmf:
                next_tree = Tree(self.tmp_path)
                next_ctx = TemplateContext(
                    tree_root=next_tree,
                    previous_ctx=self,
                    recursive=self.recursive,
                )
                next_ctx.generate(output)
            else:
                # Otherwise move the final
                shutil.copytree(
                    self.tmp_path,
                    output,
                    symlinks=True,
                    dirs_exist_ok=True,
                )
