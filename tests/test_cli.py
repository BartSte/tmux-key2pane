import sys
from argparse import ArgumentParser, Namespace

from key2pane.cli import make_parser
from key2pane.settings import load_config, make_settings
from key2pane.tmux import Pane
from tests import paths
from tests.helpers import monkeypatch_tmux


def test_make_parser_defaults(restore_argv):
    sys.argv = ["key2pane", "Hello", "Enter"]
    parser: ArgumentParser = make_parser()
    args: Namespace = parser.parse_args()
    fields: list[str] = ["config", "logfile", "loglevel", "keys"]
    assert all(hasattr(args, field) for field in fields)
    assert args.keys == ["Hello", "Enter"]


def test_make_parser_options(restore_argv):
    sys.argv = [
        "key2pane",
        "-c",
        "config.json",
        "-s",
        "foo",
        "-w",
        "0",
        "-i",
        "1",
        "--logfile",
        "log.log",
        "--loglevel",
        "DEBUG",
        "Hello",
        "Enter",
    ]
    parser: ArgumentParser = make_parser()
    args: Namespace = parser.parse_args()

    assert args.config == "config.json"
    assert args.session == "foo"
    assert args.window == 0
    assert args.index == 1
    assert args.logfile == "log.log"
    assert args.loglevel == "DEBUG"
    assert args.keys == ["Hello", "Enter"]


def test_update_args(restore_argv, monkeypatch):
    monkeypatch_tmux(monkeypatch)
    sys.argv = ["key2pane", "Hello", "Enter"]
    old: Namespace = make_parser().parse_args()
    config: dict = load_config(paths.config)
    active_pane: Pane = Pane("foo", 0, 0)
    new = make_settings(old, active_pane, config)

    assert new.config == old.config
    assert new.session == "foo"
    assert new.window == 0
    assert new.index == 0
    assert new.logfile == "log.log"
    assert new.loglevel == "DEBUG"
    assert new.keys == ["Hello", "Enter"]
