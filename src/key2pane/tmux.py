import logging
import subprocess
from typing import Generator


def execute(*args) -> str:
    try:
        return subprocess.check_output(["tmux", *args]).decode("utf-8").strip()
    except subprocess.CalledProcessError as error:
        logging.critical(error.output.decode("utf-8"))
        raise


class Pane:
    SEP: str = ":"

    def __init__(self, session: str, window: int, index: int):
        self._session: str = session
        self._window: int = window
        self._index: int = index
        self._command: str = self._find_command()

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

    def as_dict(self) -> dict[str, str | int]:
        return {
            "session": self.session,
            "window": self.window,
            "index": self.index,
            "command": self.command,
        }

    @classmethod
    def from_active(cls) -> "Pane":
        stdout: str = execute(
            "display-message", "-p", f"#S{cls.SEP}#I{cls.SEP}#P"
        )
        session, window, pane = stdout.split(cls.SEP)
        return cls(session, int(window), int(pane))

    def _find_command(self) -> str:
        stdout: str = execute(
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

    def __repr__(self) -> str:
        return (
            f"{self.session}{self.SEP}{self.window}{self.SEP}{self.index}"
            f"{self.SEP}{self.command}"
        )

    def __str__(self) -> str:
        return self.__repr__()

    def __eq__(self, other: object) -> bool:
        return str(self) == str(other)
