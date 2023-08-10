import click
from click import Context

from fmf_jinja import __version__


@click.group("fmf-jinja")
@click.version_option(__version__, message="%(version)s")
def main(ctx: Context) -> None:
    """
    FMF-Jinja template generator
    """
    pass
