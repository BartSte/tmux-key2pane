import logging
import subprocess
from typing import Generator


class TmuxError(Exception):
    """Raised when a tmux command fails."""


def execute(*args) -> str:
    """Execute a tmux command and return the output.

    Args:
        *args: the arguments to pass to tmux.

    Raises:
        TmuxError: when tmux command fails.

    Returns:
        stdout of the tmux command.
    """
    try:
        return subprocess.check_output(["tmux", *args]).decode("utf-8").strip()
    except subprocess.CalledProcessError as error:
        logging.critical(error.output.decode("utf-8"))
        raise TmuxError(f"tmux {' '.join(args)} failed") from error


class Pane:
    """A class to represent a tmux pane."""

    def __init__(self, session: str, window: int, index: int):
        """Initialize the Pane.

        Args:
            session: the session of the pane.
            window: the window of the pane.
            index: the index of the pane.
        """
        self._session: str = session
        self._window: int = window
        self._index: int = index
        self._command: str = self._find_command()

    def _find_command(self) -> str:
        """Based on the session, window, and index, find the command running in
        the pane.

        Raises:
            TmuxError: when the pane is not using the `tmux list-panes` command.

        Returns:
            the command running in the pane.
        """
        stdout: str = execute(
            "list-panes",
            "-t",
            f"{self.session}:{self.window}",
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

        raise TmuxError(f"Current pane not found in {index_vs_commands}")

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
        """Represent the Pane as a dictionary.

        Returns:
            a dictionary representation of the Pane.
        """
        return {
            "session": self.session,
            "window": self.window,
            "index": self.index,
            "command": self.command,
        }

    def send(self, keys: list[str], reset: bool = True) -> str:
        """Send keys to the pane.

        If reset is True, the keys are sent after sending a C-c to the pane.
        This is done separately as sending it together with other keys does not
        work smoothly when vim bindings are used on the command line of
        bash/zsh.

        Args:
            keys: the keys to send.

        Returns:
            stdout of the tmux command which is typically empty.
        """
        cmd: tuple[str, ...] = ("send-keys", "-t", str(self))
        if reset:
            logging.debug("Resetting pane by sending C-c")
            execute(*cmd, "C-c")

        logging.info("Sent keys: %s", keys)
        return execute(*cmd, *keys)

    @classmethod
    def from_active(cls) -> "Pane":
        """Create a Pane object from the active pane.

        Returns:
            a Pane object representing the active pane.
        """
        stdout: str = execute("display-message", "-p", "#S:#I:#P")
        session, window, pane = stdout.split(":")
        return cls(session, int(window), int(pane))

    def __str__(self) -> str:
        """The string representation of the Pane corresponds to the notation
        used in tmux.

        Returns:
            the string representation of the Pane.
        """
        return f"{self.session}:{self.window}.{self.index}"

    def __eq__(self, other: object) -> bool:
        """If the string representation of the Pane is equal to the string
        representation of another Pane, they are considered equal.

        Args:
            other: another object.

        Returns:
            True if the string representations are equal, False otherwise.
        """
        return isinstance(other, Pane) and str(self) == str(other)
