from importlib.metadata import version

from utils import call_cli


def test_base_help() -> None:
    result = call_cli(parameters=["--help"])
    assert result.exit_code == 0
    assert "Usage: fmf-jinja [OPTIONS] COMMAND [ARGS]..." in result.output


def test_base_version() -> None:
    # This test requires packit on pythonpath
    result = call_cli(parameters=["--version"])
    assert result.exit_code == 0
    assert result.output.strip() == version("fmf-jinja")
