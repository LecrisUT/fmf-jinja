from click.testing import CliRunner, Result

from click.core import BaseCommand
from pathlib import Path
from typing import Union, Optional

from fmf_jinja.cli.main import main
from fmf_jinja.cli.utils import cd


def call_cli(
    fnc: BaseCommand = main,
    parameters: Optional[list[str]] = None,
    envs: Optional[dict[str, Optional[str]]] = None,
    working_dir: Union[str, Path] = ".",
) -> Result:
    runner = CliRunner()
    envs = envs or {}
    parameters = parameters or []
    # catch exceptions enables debugger
    with cd(working_dir):
        return runner.invoke(fnc, args=parameters, env=envs, catch_exceptions=False)
