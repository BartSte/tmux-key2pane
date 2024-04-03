import json
import logging
from dataclasses import dataclass
from os.path import exists
from typing import Any


def load_config(path: str) -> dict:
    if not exists(path):
        logging.warning("Config file not found at %s", path)
        return {}

    with open(path) as file:
        return json.load(file)


@dataclass
class Settings:
    index: int
    window: int
    session: str
    actions: list[dict[str, str | list[str]]]

    @classmethod
    def from_dicts(cls, *dicts: dict[str, Any]) -> "Settings":
        """Create a Settings object from a tuple of dictionaries.

        The order of the dictionaries determines the precedence of values. The
        first dictionary has the lowest precedence, the last dictionary the
        highest. This means that if the same key is present in multiple
        dictionaries, the value from the last dictionary will be used. If the
        value is None, it will not be used.

        Args:
            args:

        Returns:

        """
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
        return set(cls.__dataclass_fields__.keys())

    @classmethod
    def _assert_keys(cls, kwargs: dict[str, Any]) -> None:
        keys: set[str] = set(kwargs.keys())
        if keys != cls.attributes():
            missing: set[str] = cls.attributes() - keys
            raise ValueError(f"Missing the following settings: {missing}")
