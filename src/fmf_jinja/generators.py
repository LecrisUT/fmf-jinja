"""
Generators that consume the template and its data.
"""

from __future__ import annotations

import abc
import functools
import shutil
from abc import abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING

import attrs
from jinja2 import Environment, FileSystemLoader

from ._compat import relative_to, walk

if TYPE_CHECKING:
    from typing import Self, TypeAlias

    from fmf import Tree

    from .template import TemplateContext

    RawDataType: TypeAlias = None | int | float | str | bool
    ListDataType: TypeAlias = list[RawDataType | "ListDataType" | "DictDataType"]
    DictDataType: TypeAlias = dict[str, RawDataType | ListDataType | "DictDataType"]
    DataType: TypeAlias = RawDataType | ListDataType | DictDataType


@attrs.define
class FullGenerator:
    """
    Main generator.

    Processes the fmf tree and generates all output files
    """

    ctx: TemplateContext
    """Current run context."""
    _sub_generators: list[SubGenerator] | None = attrs.field(init=False, default=None)
    """See :py:attrs:`sub_generators`"""

    @property
    def curr_path(self) -> str:
        """Current path string that is being processed."""
        return self.ctx.curr_path

    @property
    def tree(self) -> Tree:
        """Current fmf tree node."""
        return self.ctx.tree

    @functools.cached_property
    def vars(self) -> dict[str, DataType]:
        """
        Data variables used in the jinja template generation.

        The dict is passed as-is to the jinja template renderer.
        """
        if "vars" not in self.tree.data:
            # If vars was not defined use the whole fmf tree content as the vars dict
            vars = self.tree.data  # noqa: A001
            # Handle templates
            vars.pop("templates", None)
            return vars
        # Otherwise use the vars node data
        return self.tree.get("vars")

    @property
    def sub_generators(self) -> list[SubGenerator]:
        """Actual generators to execute."""
        if self._sub_generators is None:
            self._sub_generators = []
            # Get the template generators
            raw_templates_data = self.tree.get("templates", ["/"])
            if not isinstance(raw_templates_data, list):
                raw_templates_data = [raw_templates_data]
            for template_data in raw_templates_data:
                self._sub_generators.append(
                    TemplateGenerator.from_fmf_data(self, template_data),
                )
            # Get the other generators only if vars was defined
            # Otherwise it is ambiguous if the data is a variable or generator data
            if "vars" in self.tree.data:
                symlink_data = self.tree.get("links", {})
                self._sub_generators.append(
                    SymlinkGenerator.from_fmf_data(self, symlink_data),
                )
                copy_data = self.tree.get("copy", {})
                self._sub_generators.append(
                    CopyGenerator.from_fmf_data(self, copy_data),
                )
        return self._sub_generators

    def generate(self) -> None:
        """
        Run the sub generators.
        """
        # Make the output path if it doesn't exist
        (self.ctx.tmp_path / self.curr_path).mkdir(parents=True, exist_ok=True)
        for generator in self.sub_generators:
            generator.generate()


@attrs.define
class SubGenerator(abc.ABC):
    """
    Generators that do the main work.
    """

    parent: FullGenerator
    """Main generator run."""

    @property
    def ctx(self) -> TemplateContext:
        """Current run context."""
        return self.parent.ctx

    @classmethod
    @abstractmethod
    def from_fmf_data(cls, parent: FullGenerator, data: DataType) -> Self:
        """
        Construct from the fmf data.
        """

    @abstractmethod
    def generate(self) -> None:
        """
        Run the generator.
        """


@attrs.define
class TemplateGenerator(SubGenerator):
    """
    Jinja template generator.

    Renders a jinja template or a whole folder.
    """

    path: Path
    """Relative path to the template folder."""
    exclude: list[Path] = attrs.field(factory=list)
    """Paths to be excluded from the template generation."""
    include_empty_folder: bool = False
    """Whether to include empty folders in the generated output."""

    @property
    def template_path(self) -> Path:
        """Resolved path of the template."""
        return self.ctx.join_path(self.path)

    @property
    def template_dir(self) -> Path:
        """Directory of the template: either `path` or its parent."""
        if self.template_path.is_dir():
            return self.template_path
        return self.template_path.parent

    @classmethod
    def from_fmf_data(  # noqa: D102
        cls,
        parent: FullGenerator,
        data: str | DictDataType,
    ) -> TemplateGenerator:
        if isinstance(data, str):
            return cls(parent=parent, path=Path(data))
        try:
            path = Path(data.get("path"))
            exclude = [Path(path) for path in data.get("exclude", [])]
            # TODO: expose `include_empty_folder` to fmf parsing
            return cls(parent=parent, path=path, exclude=exclude)
        except Exception as err:
            msg = f"Unsupported input data [{type(data)}]: {data}"
            raise TypeError(msg) from err

    def _render_or_copy(
        self,
        input_file: Path,
        output_dir: Path,
        env: Environment,
    ) -> None:
        """
        Render or copy the file.

        If the file has a final `.j2`suffix it is treated as a template and rendered
        otherwise it simply copies the file.

        :param input_file: original file to be copied or rendered
        :param output_dir: output directory where to create the files
        :param env: current jinja environment
        """
        if ".j2" in input_file.suffix:
            # Render the jinja template file
            # TODO: Ignore if it's a template input
            tpl = env.get_template(str(input_file.relative_to(self.template_dir)))
            output_file_name = input_file.name.removesuffix(".j2")
            output_file = output_dir / output_file_name
            with output_file.open("w") as f:
                f.write(tpl.render(self.parent.vars))
            if ".fmf" in output_file.suffixes:
                self.ctx.generated_fmf = True
            return
        # If it's not a template simply copy the file
        output_file = output_dir / input_file.name
        if input_file.is_symlink():
            # If it's a symlink generate an equivalent symlink
            output_file.unlink(missing_ok=True)
            symlink_target = input_file.resolve()
            # Check if symlink target points to a file in the template directory
            if symlink_target.is_relative_to(self.template_dir.resolve()):
                # Maintain the relative target paths if it's within the template_dir
                target_path = symlink_target.relative_to(self.template_dir.resolve())
            else:
                # Otherwise point to the resolved absolute path
                # TODO: log warning
                target_path = symlink_target
            output_file.symlink_to(target_path)
            return
        # Otherwise copy the contents of the file
        shutil.copy(input_file, output_file)

    def generate(self) -> None:  # noqa: D102
        if not self.template_path.exists():
            msg = f"Template path not found: {self.path}"
            raise FileNotFoundError(msg)
        # Use the template path as the root for the jinja templates
        env = self.ctx.jinja_env.overlay(loader=FileSystemLoader(self.template_dir))
        if not self.template_path.is_dir():
            # If path points to a file render or copy that file
            self._render_or_copy(self.template_path, self.ctx.output_path, env=env)
        else:
            # Otherwise generate the whole directory rendering or copying the files
            for curr_path, dirs_str, files_str in walk(self.template_path):
                # Generate the output path and make sure it exists
                rel_path = curr_path.relative_to(self.template_path)
                output_path = self.ctx.output_path / rel_path
                # If we don't need the empty folders, the parent directories will be
                # created as needed. `.fmf` folder is a special case where we don't
                # include it since it might not be part of the templated folder.
                if self.include_empty_folder and output_path.name != ".fmf":
                    output_path.mkdir(parents=True, exist_ok=True)
                # Exclude all directories from recursive walk
                for dir in dirs_str:  # noqa: A001
                    if rel_path / dir in self.exclude:
                        dirs_str.remove(dir)
                # Loop over all the files copying or rendering the templates
                for file in files_str:
                    file_path = rel_path / file
                    # Skip fmf source files because they were handled previously
                    if file_path in self.ctx.fmf_files:
                        continue
                    # Skip any files that were requested to be skipped
                    if file_path in self.exclude:
                        continue
                    output_path.mkdir(parents=True, exist_ok=True)
                    # Pass the resolved absolute path of the file
                    self._render_or_copy(curr_path / file, output_path, env=env)


@attrs.define
class SymlinkGenerator(SubGenerator):
    """
    Symbolic link generator.

    Creates symbolic links with the context of the fmf tree.
    """

    symlinks: dict[str, Path]
    """
    Symbolic links to generate

    The dict structure is:
      - key: path to the symbolic link generated
      - value: target where the symbolic link points to
    """

    @classmethod
    def from_fmf_data(  # noqa: D102
        cls,
        parent: FullGenerator,
        data: dict[str, str],
    ) -> SymlinkGenerator:
        return cls(
            parent=parent,
            symlinks={
                output_symlink: Path(symlink_target)
                for output_symlink, symlink_target in data.items()
            },
        )

    def generate(self) -> None:  # noqa: D102
        for output_symlink_str, symlink_target in self.symlinks.items():
            output_symlink = self.ctx.output_path / output_symlink_str
            if symlink_target.is_absolute():
                # If the symlink target is absolute, then it starts from the output_path
                target_path = self.ctx.output_path / str(symlink_target).removeprefix(
                    "/",
                )
            else:
                # Otherwise it starts from the current output path
                target_path = self.ctx.output_path / symlink_target
            # Make sure the symlink is created with relative path structure
            relative_target_path = relative_to(
                target_path,
                output_symlink,
                walk_up=True,
            )
            # Makes sure parent directory is created
            output_symlink.parent.mkdir(exist_ok=True)
            # Remove any pre-existing symlinks or files
            output_symlink.unlink(missing_ok=True)
            # Create the symlink
            output_symlink.symlink_to(relative_target_path)


@attrs.define
class CopyGenerator(SubGenerator):
    """
    Copy generator.

    Copies files with the context of the fmf tree.
    """

    files: dict[str, Path]
    """Files to copy."""

    @classmethod
    def from_fmf_data(  # noqa: D102
        cls,
        parent: FullGenerator,
        data: dict[str, str],
    ) -> CopyGenerator:
        return cls(
            parent=parent,
            files={dest: Path(src) for dest, src in data.items()},
        )

    def generate(self) -> None:  # noqa: D102
        for dest_str, src in self.files.items():
            dest_path = self.ctx.join_path(Path(dest_str), self.ctx.tmp_path)
            actual_src = self.ctx.join_path(src)
            if not actual_src.exists():
                msg = f"File not found: {actual_src}"
                raise FileNotFoundError(msg)
            if actual_src.is_dir():
                shutil.copytree(actual_src, dest_path)
            else:
                shutil.copy(actual_src, dest_path)
