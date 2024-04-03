import json
import logging
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from os.path import exists, expanduser

_DESCRIPTION: str = """
Sends a sequence of keys to any tmux pane, based on the pane's current command.

Which keys to send, must be specified in a json with the following format:

{
  "actions": [
    {
      "command": "bash|zsh|fish",
      "keys": ["echo 'Hello, World!'", "Enter"]
    }
  ],

  // other configurations

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

