import subprocess
import sys

from tests import paths


def execute(*args):
    try:
        return (
            subprocess.check_output(
                ["python3", "-m", "key2pane", "--dry-run", *args],
                stderr=subprocess.STDOUT,
                executable=sys.executable,
            )
            .decode("utf-8")
            .strip()
        )
    except subprocess.CalledProcessError as error:
        return error.output.decode("utf-8")


def test_help(tmux_check):
    stdout: str = execute("-h")
    assert "usage: __main__.py" in stdout


def test_no_config(tmux_check):
    stdout: str = execute("--config", "/foo/bar/baz.toml")
    assert "Config file not found" in stdout, stdout


def test_invalid_config(tmux_check):
    stdout: str = execute("--config", "/dev/null")
    assert "Invalid config file" in stdout, stdout


def test_invalid_args_or_tmux_not_running(tmux_check):
    stdout: str = execute("--config", paths.config)
    assert "Hello, World!" in stdout
