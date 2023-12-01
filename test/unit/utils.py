from __future__ import annotations

from typing import TYPE_CHECKING

from click.testing import CliRunner, Result

from fmf_jinja.cli.main import main
from fmf_jinja.cli.utils import cd

if TYPE_CHECKING:
    from pathlib import Path

    from click.core import BaseCommand


def call_cli(
    fnc: BaseCommand = main,
    parameters: list[str] | None = None,
    envs: dict[str, str | None] | None = None,
    working_dir: str | Path = ".",
) -> Result:
    runner = CliRunner()
    envs = envs or {}
    parameters = parameters or []
    # catch exceptions enables debugger
    with cd(working_dir):
        return runner.invoke(fnc, args=parameters, env=envs, catch_exceptions=False)
