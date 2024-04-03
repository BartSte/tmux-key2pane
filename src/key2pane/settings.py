import json
import logging
from argparse import Namespace
from os.path import exists
from typing import Any, Generator

from key2pane.tmux import Pane


def load_config(path: str) -> dict:
    if not exists(path):
        logging.warning("Config file not found at %s", path)
        return {}

    with open(path) as file:
        return json.load(file)


def make_settings(
    args: Namespace, pane: Pane, config: dict[str, Any]
) -> Namespace:
    args = _merge(args, config)
    args = _add_missing(args, pane)
    assert all(x is not None for x in vars(args).values())
    return args


def _merge(args: Namespace, config: dict[str, Any]) -> Namespace:
    no_actions: Generator = (
        (k, v) for k, v in config.items() if k != "actions"
    )
    no_none: Generator = ((k, v) for k, v in no_actions if v is not None)
    for key, value in no_none:
        setattr(args, key, value)
        logging.debug("Updated %s to %s", key, value)
    return args


def _add_missing(args: Namespace, pane: Pane) -> Namespace:
    attributes: list[str] = ["session", "window", "index"]
    missing: Generator = (x for x in attributes if getattr(args, x) is None)
    for attribute in missing:
        setattr(args, attribute, getattr(pane, attribute))

    return args
