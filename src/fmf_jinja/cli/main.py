import click
from click import Context

from fmf_jinja import __version__


@click.group()
@click.version_option(__version__)
def main(ctx: Context) -> None:
    """
    FMF-Jinja template generator
    """
    pass
