import sys
from argparse import ArgumentParser, Namespace

from key2pane.__main__ import make_settings
from key2pane.cli import make_parser
from key2pane.settings import Settings
from tests import paths


def test_make_settings(restore_argv, monkeypatch_tmux):
    """Encountered a bug where the reset was True in the config but the cli arg
    was False. Thus the reset was set to False, which is unexpected."""
    sys.argv = ["key2pane", "--config", paths.config_reset]
    parser: ArgumentParser = make_parser()
    args: Namespace = parser.parse_args()
    settings: Settings = make_settings(args)
    assert settings.reset is True
    assert args.reset is False
