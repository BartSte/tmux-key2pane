import logging
import sys
from subprocess import STDOUT, CalledProcessError, check_output

import pytest


@pytest.fixture(scope="function")
def restore_argv():
    old_argv = sys.argv
    yield "restore_argv"
    logging.debug("Restoring sys.argv from %s to %s", sys.argv, old_argv)
    sys.argv = old_argv


def patch_tmux_execute(*args) -> str:
    if "display-message" in args:
        return "foo:0:0"

    elif "list-panes" in args:
        return "0:bash"

    elif "send-keys" in args:
        return " ".join(args)

    else:
        raise ValueError(f"Unknown command: {args}")


@pytest.fixture(scope="function")
def monkeypatch_tmux(monkeypatch):
    monkeypatch.setattr("key2pane.tmux.execute", patch_tmux_execute)


@pytest.fixture(scope="function")
def tmux_check():
    """Skip tests if tmux is not running."""
    try:
        return (
            check_output(["tmux", "list-panes"], stderr=STDOUT)
            .decode("utf-8")
            .strip()
        )
    except CalledProcessError as error:
        pytest.skip(f"tmux not running: {error.output.decode('utf-8')}")
    except FileNotFoundError as error:
        pytest.skip(f"tmux not installed: {error}")
