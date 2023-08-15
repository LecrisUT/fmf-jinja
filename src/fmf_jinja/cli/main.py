import click
from click import Context
from pathlib import Path

from fmf_jinja import __version__
from fmf_jinja.fmf import Tree
from fmf_jinja.template import generate as _generate


@click.group("fmf-jinja")
@click.version_option(__version__, message="%(version)s")
@click.option(
    "-r",
    "--root",
    metavar="PATH",
    type=Path,
    default=".",
    show_default=True,
    help="Path to the metadata tree root.",
)
@click.pass_context
def main(ctx: Context, root: Path) -> None:
    """
    FMF-Jinja template generator
    """
    ctx.ensure_object(dict)
    ctx.obj["tree"] = Tree(root)


@main.command()
@click.option(
    "-o",
    "--output",
    metavar="PATH",
    type=Path,
    default=".",
    show_default=True,
    help="Path to generated output directory",
)
@click.pass_context
def generate(ctx: Context, output: Path) -> None:
    """
    Generate template output
    \f

    :param ctx: Click context
    :param output: Output path
    :return:
    """
    _generate(ctx.obj["tree"], output)
