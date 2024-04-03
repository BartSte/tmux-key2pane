#!/usr/bin/env python3

from argparse import ArgumentParser, Namespace, RawDescriptionHelpFormatter
import logging
from os import environ
from os.path import expanduser
import subprocess
from typing import Generator

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


class Tmux:
    def __init__(self, pane: "Pane | None" = None):
        self._destination_pane: Pane | None = pane
        self._active_pane: Pane = Pane.from_active()

    @staticmethod
    def command(*args) -> str:
        return subprocess.check_output(["tmux", *args]).decode("utf-8").strip()

    @property
    def active_pane(self) -> "Pane":
        return self._active_pane

    @property
    def destination_pane(self) -> "Pane | None":
        return self._destination_pane

    @destination_pane.setter
    def destination_pane(self, pane: "Pane | None"):
        self._destination_pane = pane


class Pane:
    SEP: str = ":"

    def __init__(self, session: str, window: int, index: int):
        self._session: str = session
        self._window: int = window
        self._index: int = index
        self._command: str = self._find_command()
        logging.debug("Pane object created: %s", self)

    @classmethod
    def from_active(cls) -> "Pane":
        stdout: str = Tmux.command(
            "display-message", "-p", f"#S{cls.SEP}#I{cls.SEP}#P"
        )
        session, window, pane = stdout.split(cls.SEP)
        return cls(session, int(window), int(pane))

    def _find_command(self) -> str:
        stdout: str = Tmux.command(
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


def make_parser(pane: Pane) -> ArgumentParser:
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
        default=pane.session,
        help="Specify the tmux session, default to current session",
    )
    parser.add_argument(
        "-w",
        "--window",
        default=environ.get("KEY2PANE_WINDOW", pane.window),
        help="Specify the tmux window. If not provided, the KEY2PANE_WINDOW "
        "environment variable will be used, if not set, the current window will"
        " be used.",
    )
    parser.add_argument(
        "-i",
        "--index",
        default=environ.get("KEY2PANE_PANE", pane.index),
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
    logger: logging.Logger = logging.getLogger()
    logger.setLevel(loglevel)

    formatter: logging.Formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler: logging.FileHandler = logging.FileHandler(logfile)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


def main():
    tmux: Tmux = Tmux()
    parser: ArgumentParser = make_parser(tmux.active_pane)
    args: Namespace = parser.parse_args()

    set_logging(args.loglevel, args.logfile)

    tmux.destination_pane = Pane(
        args.session, int(args.window), int(args.index)
    )


if __name__ == "__main__":
    main()
