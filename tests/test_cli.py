import sys
from argparse import ArgumentParser, Namespace

from key2pane.cli import make_parser


def test_make_parser_defaults(restore_argv):
    sys.argv = ["key2pane", "Hello", "Enter"]
    parser: ArgumentParser = make_parser()
    args: Namespace = parser.parse_args()
    fields: list[str] = [
        "config",
        "logfile",
        "loglevel",
        "positional",
        "reset",
    ]
    assert all(hasattr(args, field) for field in fields)
    assert args.positional == ["Hello", "Enter"]


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
        "--reset",
        "Hello",
        "Enter",
    ]
    parser: ArgumentParser = make_parser()
    args: Namespace = parser.parse_args()

    assert args.config == "config.json"
    assert args.session == "foo"
    assert args.window == 0
    assert args.index == 1
    assert args.reset is True
    assert args.logfile == "log.log"
    assert args.loglevel == "DEBUG"
    assert args.positional == ["Hello", "Enter"]
