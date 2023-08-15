import os
import shutil
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Union

from fmf import Tree


def _generate(tree: Tree, output: Path, output_root: Path) -> None:
    # Get the template files/folders
    templates: Union[str, list[str]] = tree["templates"]  # type: ignore[assignment]
    if not isinstance(templates, list):
        templates = [templates]
    # Get the vars used in the template
    vars = tree.get("vars", {})
    assert isinstance(vars, dict)
    # Get the symlinks to generate
    links = tree.get("links", {})
    assert isinstance(links, dict)
    # Make the root output path if it doesn't exist
    output.mkdir(parents=True, exist_ok=True)
    assert tree.root is not None
    # Loop over all templates files/folders
    for tpl_str in templates:
        tpl_path = Path(tpl_str)
        # Drop root ('/') to make it relative to tree.root
        if tpl_path.is_absolute():
            tpl_path = Path(*tpl_path.parts[1:])
        # Create the absolute path including the tree.root
        tpl_path = tree.root / tpl_path
        if not tpl_path.exists():
            raise FileNotFoundError(f"Template path not found: {tpl_str} ({tpl_path})")
        # Create the jinja environment that will load the
        loader = FileSystemLoader(tpl_path if tpl_path.is_dir() else tpl_path.parent)
        env = Environment(loader=loader)
        if tpl_path.is_dir():
            # If it's a directory, loop over the file structure
            for path_str, _, files_str in os.walk(tpl_path):
                # Generate the output path and make sure it exists
                rel_path = Path(path_str).relative_to(tpl_path)
                output_path = output / rel_path
                output_path.mkdir(parents=True, exist_ok=True)
                # Loop over all the files copying or rendering the templates
                for fil in [Path(f) for f in files_str]:
                    if ".j2" not in fil.suffixes:
                        # If it's not a template simply copy the file
                        input_file = tpl_path / rel_path / fil
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
                            [part for part in fil.name.split(".") if part != "j2"]
                        )
                        with output_file.open("w") as f:
                            f.write(tpl.render(**vars))
        else:
            # If it's a file treat it as a template and output it to the output root
            tpl = env.get_template(tpl_path.name)
            # Strip the .j2 suffix if it exists
            fil_name = ".".join(
                [part for part in tpl_path.name.split(".") if part != "j2"]
            )
            output_file = output / fil_name
            with output_file.open("w") as f:
                f.write(tpl.render(**vars))
    # Create the symlinks
    for link_name, link_path_str in links.items():
        assert type(link_name) == str
        assert type(link_path_str) == str
        link_path = Path(link_path_str)
        # If the link path is absolute treat it as relative to the output root
        if link_path.is_absolute():
            link_path = output_root / Path(*link_path.parts[1:])
        output_link = output / link_name
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
    Generate a template from fmf metadata

    :param tree: FMF metadata tree
    :param output: Output path
    """
    # Currently only generating on leaves

    for curr_tree, branches, leaves in tree.walk():
        for leaf_tree in [curr_tree[f"/{leaf}"] for leaf in leaves]:
            assert isinstance(leaf_tree, Tree)
            _generate(
                leaf_tree, output / leaf_tree.name.removeprefix("/"), output.absolute()
            )
