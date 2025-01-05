import sys
from argparse import ArgumentParser, Namespace

from key2pane.__main__ import make_settings
from key2pane.cli import make_parser
from key2pane.settings import Settings
from tests import paths


def test_reset_cli_none(restore_argv, monkeypatch_tmux):
    """Encountered a bug where the reset was True in the config but the cli arg
    was False. Thus the reset was set to False, which is unexpected."""
    sys.argv = ["key2pane", "--config", paths.config_reset]
    parser: ArgumentParser = make_parser()
    args: Namespace = parser.parse_args()
    settings: Settings = make_settings(args)
    assert args.reset is None
    assert settings.reset is True

def test_reset_cli_true(restore_argv, monkeypatch_tmux):
    sys.argv = ["key2pane", "--config", paths.config_reset, "--reset"]
    parser: ArgumentParser = make_parser()
    args: Namespace = parser.parse_args()
    settings: Settings = make_settings(args)
    assert args.reset is True
    assert settings.reset is True

def test_reset_cli_false(restore_argv, monkeypatch_tmux):
    sys.argv = ["key2pane", "--config", paths.config_reset, "--noreset"]
    parser: ArgumentParser = make_parser()
    args: Namespace = parser.parse_args()
    settings: Settings = make_settings(args)
    assert args.reset is False
    assert settings.reset is False
