from importlib.metadata import version

from click.testing import CliRunner

from fmf_jinja.cli import main


def test_base_help() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "Usage: fmf-jinja [OPTIONS] COMMAND [ARGS]..." in result.output


def test_base_version() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["--version"])
    assert result.exit_code == 0
    assert result.output.strip() == version("fmf-jinja")
