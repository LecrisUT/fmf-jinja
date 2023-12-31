"""Module for the Template fmf data type."""

from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import TYPE_CHECKING

from jinja2 import Environment, FileSystemLoader

if TYPE_CHECKING:
    from fmf.typing import DataType

from fmf import Tree
from fmf.normalize import normalize


class Template:
    """
    Template fmf data type.

    Contains the template folder to be generated by `fmf-jinja`
    """

    path: Path
    """Path to the template folder."""
    exclude: list[Path]
    """Paths to be excluded from the template generation."""

    def __init__(self, data: DataType, root: str) -> None:  # noqa: D107
        self.exclude = []
        if isinstance(data, str):
            self.path = normalize(Path, data, root, normalizer=self.normalize_path)
            return
        if isinstance(data, dict):
            path = data["path"]
            if not isinstance(path, str):
                msg = f"Unexpected type for item path: expected str, got {type(path)}"
                raise TypeError(msg)
            try:
                self.path = normalize(Path, path, root, normalizer=self.normalize_path)
                if "exclude" in data:
                    self.exclude = normalize(list[Path], data["exclude"])
            except TypeError as err:
                msg = f"Unsupported input data: {data}"
                raise TypeError(msg) from err
        else:
            msg = f"Unsupported input data: [{type(data)}] {data}"
            raise TypeError(msg)

    @staticmethod
    def normalize_path(path_str: str, root: str) -> Path:
        """
        Normalize the path to absolute path.

        :param path_str: path string to normalize
        :param root: path root
        :return: normalized absolute Path
        """
        path = Path(path_str)
        # Drop root ('/') to make it relative to tree.root
        if path.is_absolute():
            path = Path(*path.parts[1:])
        # Return the absolute path including the tree.root
        return root / path


# TODO: Resolve PLR issues
def _generate(tree: Tree, output: Path, output_root: Path) -> None:  # noqa: PLR0912, PLR0915
    # Get the vars used in the template
    tree_vars = tree.get("vars", {})
    assert isinstance(tree_vars, dict)
    # Get the symlinks to generate
    links = tree.get("links", {})
    assert isinstance(links, dict)
    # Make the root output path if it doesn't exist
    output.mkdir(parents=True, exist_ok=True)
    assert tree.root is not None
    # Loop over all templates files/folders
    templates = tree.normalize(list[Template], "templates", tree.root)
    assert isinstance(templates, list)
    for template in templates:
        if not template.path.exists():
            msg = f"Template path not found: {template.path}"
            raise FileNotFoundError(msg)
        # Create the jinja environment that will load the
        loader = FileSystemLoader(
            template.path if template.path.is_dir() else template.path.parent,
        )
        env = Environment(
            loader=loader,
            keep_trailing_newline=True,
            trim_blocks=True,
            autoescape=True,
        )
        if template.path.is_dir():
            # If it's a directory, loop over the file structure
            for path_str, dirs_str, files_str in os.walk(template.path):
                # Generate the output path and make sure it exists
                rel_path = Path(path_str).relative_to(template.path)
                output_path = output / rel_path
                output_path.mkdir(parents=True, exist_ok=True)
                # Exclude all directories from recursive walk
                for d in dirs_str:
                    if rel_path / d in template.exclude:
                        dirs_str.remove(d)
                # Loop over all the files copying or rendering the templates
                for fil in [
                    Path(f) for f in files_str if rel_path / f not in template.exclude
                ]:
                    if ".j2" not in fil.suffixes:
                        # If it's not a template simply copy the file
                        input_file = template.path / rel_path / fil
                        output_file = output_path / fil
                        if input_file.is_symlink():
                            # If it's a symlink copy as is
                            if output_file.is_symlink():
                                # Remove existing symlink if it points to somewhere else
                                if output_file.readlink() == input_file.readlink():
                                    continue
                                output_file.unlink()
                            elif output_file.exists():
                                # If it's a file always remove it
                                output_file.unlink()
                            output_file.symlink_to(input_file.readlink())
                        else:
                            # Otherwise copy the contents of the file
                            shutil.copy(input_file, output_file)
                    else:
                        # Otherwise render the file
                        # TODO: Ignore if it's a template input
                        tpl = env.get_template(str(rel_path / fil))
                        output_file = output_path / ".".join(
                            [part for part in fil.name.split(".") if part != "j2"],
                        )
                        with output_file.open("w") as f:
                            f.write(tpl.render(**tree_vars))
        else:
            # If it's a file treat it as a template and output it to the output root
            tpl = env.get_template(template.path.name)
            # Strip the .j2 suffix if it exists
            fil_name = ".".join(
                [part for part in template.path.name.split(".") if part != "j2"],
            )
            output_file = output / fil_name
            with output_file.open("w") as f:
                f.write(tpl.render(**tree_vars))
    # Create the symlinks
    for link_name, link_path_str in links.items():
        assert isinstance(link_name, str)
        assert isinstance(link_path_str, str)
        link_path = Path(link_path_str)
        # If the link path is absolute treat it as relative to the output root
        if link_path.is_absolute():
            link_path = output_root / Path(*link_path.parts[1:])
        output_link = output / link_name
        # Makes sure paren directory is created
        output_link.parent.mkdir(exist_ok=True)
        if output_link.is_symlink():
            # Remove existing symlink if it points to somewhere else
            if output_link.readlink() == link_path:
                continue
            output_link.unlink()
        elif output_link.exists():
            # If it's a file always remove it
            output_link.unlink()
        output_link.symlink_to(link_path)


def generate(tree: Tree, output: Path) -> None:
    """
    Generate a template from fmf metadata.

    :param tree: FMF metadata tree
    :param output: Output path
    """
    # Currently only generating on leaves

    for curr_tree, _, leaves in tree.walk():
        for leaf_tree in [curr_tree[f"/{leaf}"] for leaf in leaves]:
            assert isinstance(leaf_tree, Tree)
            _generate(
                leaf_tree,
                output / leaf_tree.name.removeprefix("/"),
                output.absolute(),
            )
