#!/usr/bin/env python3

import json
import logging
import subprocess
from argparse import ArgumentParser, Namespace, RawDescriptionHelpFormatter
from os.path import exists, expanduser
from typing import Any, Generator

_DESCRIPTION: str = """
Sends a sequence of keys to any tmux pane, based on the pane's current command.

Which keys to send, must be specified in a json with the following format:

{
    "bash|zsh|fish": ["echo hello_world", "Enter"],
}

here, the key is the regex that will be matched against the current pane's
command. The value is an array of arguments that will be applied to the `tmux
send-keys` command. In the example above, if the current pane is running bash,
zsh, or fish, then the command `echo hello_world` will be sent to the pane.
Finally the command `Enter` will be sent to the pane, which has a special effect
for the `tmux send-keys` command, as it will simulate pressing the Enter key,
instead of literally typing the word Enter.

The positional arguments passed to this script can be used to populate
placeholders in the json values. The placeholders are curly braces with an
optional number inside, where the number indicates which argument to use,
starting from 1. So {1} will be replaced by the first argument, {2} by the
second, and so on. If no number is provided, all the arguments will be used. For
example, if the command is: `key2pane foo bar`, and the json value is: `echo {1}
{2}`, then the following keys will be sent to the pane: `echo foo bar`.

The curly braces can be escaped by using a backslash. For example, {1} will be
replaced by {1}, and not by the first argument.
"""


def main():
    try:
        _main()
    except Exception as error:
        logging.critical(error)


def _main():
    args: Namespace = make_parser().parse_args()
    set_logging(args.loglevel, args.logfile)
    logging.debug("Parsed args: %s", args)

    active_pane: Pane = Pane.from_active()
    logging.debug("Active pane: %s", active_pane)

    config: dict = load_config(args.config)
    logging.debug("Config: %s", config)

    args = update_args(args, active_pane, config)
    logging.debug("Arguments: %s", args)

    destination_pane: Pane = Pane(args.session, args.window, args.index)
    logging.info("Destination pane: %s", destination_pane)


def make_parser() -> ArgumentParser:
    parser: ArgumentParser = ArgumentParser(
        description=_DESCRIPTION, formatter_class=RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "-c",
        "--config",
        default=expanduser("~/.config/key2pane/config.json"),
        help="The path to the config file. The default is "
        "~/.config/key2pane/config.json",
    )
    parser.add_argument(
        "-s",
        "--session",
        help="Specify the tmux session, default to current session",
    )
    parser.add_argument(
        "-w",
        "--window",
        type=int,
        help="Specify the tmux window. If not provided, the KEY2PANE_WINDOW "
        "environment variable will be used, if not set, the current window will"
        " be used.",
    )
    parser.add_argument(
        "-i",
        "--index",
        type=int,
        help="Specify the tmux pane index. If not provided, the KEY2PANE_PANE "
        "environment variable will be used, if not set, the current pane its "
        "index will be used.",
    )
    parser.add_argument(
        "--logfile",
        default=expanduser("~/.local/state/key2pane.log"),
        help="Specify the log file",
    )
    parser.add_argument(
        "--loglevel",
        default="WARNING",
        help="Specify the log level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
    )
    parser.add_argument("keys", nargs="*", help="The keys to send to the pane")
    return parser


def set_logging(loglevel: str, logfile: str) -> None:
    logging.debug("Initializing logging by printing this message")
    logger: logging.Logger = logging.getLogger()
    logger.setLevel(loglevel)

    formatter: logging.Formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler: logging.FileHandler = logging.FileHandler(logfile)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


def load_config(path: str) -> dict:
    if not exists(path):
        logging.warning("Config file not found at %s", path)
        return {}

    with open(path) as file:
        return json.load(file)


class Pane:
    SEP: str = ":"

    def __init__(self, session: str, window: int, index: int):
        self._session: str = session
        self._window: int = window
        self._index: int = index
        self._command: str = self._find_command()

    @classmethod
    def from_active(cls) -> "Pane":
        stdout: str = tmux(
            "display-message", "-p", f"#S{cls.SEP}#I{cls.SEP}#P"
        )
        session, window, pane = stdout.split(cls.SEP)
        return cls(session, int(window), int(pane))

    def _find_command(self) -> str:
        stdout: str = tmux(
            "list-panes",
            "-t",
            f"{self.session}{self.SEP}{self.window}",
            "-F",
            "#{pane_index}:#{pane_current_command}",
        )
        splitted: Generator = (line.split(":") for line in stdout.splitlines())
        index_vs_commands: Generator = (
            (
                int(index),
                command,
            )
            for index, command in splitted
        )

        for index, command in index_vs_commands:
            if int(index) == self.index:
                return command

        logging.error("Current pane not found in %s", index_vs_commands)
        return ""

    @property
    def session(self) -> str:
        return self._session

    @property
    def window(self) -> int:
        return self._window

    @property
    def index(self) -> int:
        return self._index

    @property
    def command(self) -> str:
        return self._command

    def __repr__(self) -> str:
        return (
            f"{self.session}{self.SEP}{self.window}{self.SEP}{self.index}"
            f"{self.SEP}{self.command}"
        )

    def __str__(self) -> str:
        return self.__repr__()

    def __eq__(self, other: object) -> bool:
        return str(self) == str(other)


def tmux(*args) -> str:
    try:
        return subprocess.check_output(["tmux", *args]).decode("utf-8").strip()
    except subprocess.CalledProcessError as error:
        logging.error(error.output.decode("utf-8"))
        raise


def update_args(
    args: Namespace, pane: Pane, config: dict[str, Any]
) -> Namespace:
    args = _update_config(args, config)
    args = _set_missing(args, pane)
    assert all(x is not None for x in vars(args).values())
    return args


def _update_config(args: Namespace, config: dict[str, Any]) -> Namespace:
    no_actions: Generator = (
        (k, v) for k, v in config.items() if k != "actions"
    )
    no_none: Generator = ((k, v) for k, v in no_actions if v is not None)
    for key, value in no_none:
        setattr(args, key, value)
        logging.debug("Updated %s to %s", key, value)
    return args


def _set_missing(args: Namespace, pane: Pane) -> Namespace:
    attributes: list[str] = ["session", "window", "index"]
    missing: Generator = (x for x in attributes if getattr(args, x) is None)
    for attribute in missing:
        setattr(args, attribute, getattr(pane, attribute))

    return args


if __name__ == "__main__":
    main()
