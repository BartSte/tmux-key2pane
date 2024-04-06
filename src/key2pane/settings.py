import json
import logging
import re
from dataclasses import dataclass
from os.path import exists
from typing import Any


class SettingsError(Exception):
    """Raised when an error occurs while handling settings."""


def load_config(path: str) -> dict:
    """Return the contents of a json file at `path` as a dictionary.

    Args:
        path: the path to the json file.

    Raises:
        SettingsError: when the file is not found or invalid.

    Returns:
        The contents of the json file as a dictionary.
    """
    if not exists(path):
        logging.warning("Config file not found at %s", path)
        raise SettingsError("Config file not found")

    with open(path) as file:
        try:
            return json.load(file)
        except json.JSONDecodeError as error:
            logging.error(error)
            raise SettingsError("Invalid config file") from error


@dataclass
class Settings:
    """Dataclass for settings.

    Attributes:
        index: the index of the pane.
        window: the window of the pane.
        session: the session of the pane.
        actions: the keys to send based on the pane's command.
        positional: the positional arguments passed to the script.
    """

    index: int
    window: int
    session: str
    reset: bool
    actions: list[dict[str, str | list[str]]]
    positional: list[str]

    def get_keys(self, command: str) -> list[str]:
        """Return the keys to send based on the `command`.

        Args:
            command: the name of the command.

        Raises:
            SettingsError: when no action is found or multiple actions are found.

        Returns:
            The keys to send.
        """
        matches: tuple[bool, ...] = tuple(
            bool(re.match(regex, command)) for regex in self.regexes
        )

        number_of_matches: int = sum(matches)
        if number_of_matches == 0:
            raise SettingsError(f"No action found for command {command}")

        elif number_of_matches > 1:
            raise SettingsError(
                f"Multiple actions found for command {command}"
            )

        else:
            logging.debug("Action found for command %s", command)
            keys: list[str] = self.all_keys[matches.index(True)]
            return self._format_keys(keys)

    def _format_keys(self, keys: list[str]) -> list[str]:
        try:
            return [key.format(*self.positional) for key in keys]
        except IndexError as error:
            raise SettingsError(
                "Not enough positional arguments to fill placeholders of the "
                f"keys: {keys}"
            ) from error

    @property
    def regexes(self) -> tuple[str, ...]:
        """All regexes to match against the pane's command.

        Returns:
            A tuple of regexes.
        """
        return tuple(
            action["regex"]
            for action in self.actions
            if isinstance(action["regex"], str)
        )

    @property
    def all_keys(self) -> tuple[list[str], ...]:
        """All lists of keys that could be sent to a pane.

        Returns:
            a tuple of lists of keys.
        """
        return tuple(
            action["keys"]
            for action in self.actions
            if isinstance(action["keys"], list)
        )

    @classmethod
    def from_dicts(cls, *dicts: dict[str, Any]) -> "Settings":
        """
        Create a Settings object from a tuple of dictionaries.

        The order of the dictionaries determines the precedence of values. The
        first dictionary has the lowest precedence, the last dictionary the
        highest. This means that if the same key is present in multiple
        dictionaries, the value from the last dictionary will be used. If the
        value is None, it will not be used.

        Args:
            *dicts: Tuple of dictionaries.

        Returns:
            Settings object.

        """
        # TODO: when the config sets the reset value to True, and it is not
        # given by the cli. The cli sets it back to false....
        kwargs: dict[str, Any] = {
            key: value
            for dictionary in dicts
            for key, value in dictionary.items()
            if value is not None and key in cls.attributes()
        }
        cls._assert_keys(kwargs)
        return cls(**kwargs)

    @classmethod
    def attributes(cls) -> set[str]:
        """All attributes of the dataclass.

        Returns:
            A set of strings representing the attributes.
        """
        return set(cls.__dataclass_fields__.keys())

    @classmethod
    def _assert_keys(cls, kwargs: dict[str, Any]) -> None:
        """Raise a SettingsError if the keys are not the same as the attributes.

        Args:
            kwargs: the keys to check.

        Raises:
            SettingsError: when the keys are not the same as the attributes.
        """
        keys: set[str] = set(kwargs.keys())
        if keys != cls.attributes():
            missing: set[str] = cls.attributes() - keys
            raise SettingsError(f"Missing the following settings: {missing}")
