import logging
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from logging.handlers import TimedRotatingFileHandler
from os import makedirs
from os.path import dirname, expanduser

_DESCRIPTION: str = """
Sends a sequence of keys to any tmux pane, based on the pane's current command.

Which keys to send, must be specified in a json with the following format:

{
    // Other settings ...

    "actions": [
        {
            "regex": "bash|zsh|fish",
            "keys": [
                "echo 'Hello, World!'",
                "Enter"
            ]
        }
    ]
}

The the regex will be matched against the current pane's command. The `keys` is
an array of arguments that will be applied to the `tmux send-keys` command. In
the example above, if the current pane is running bash, zsh, or fish, then the
command `echo 'Hello, World!'` will be sent to the pane. Finally the command
`Enter` will be sent to the pane, which has a special effect for the `tmux
send-keys` command, as it will simulate pressing the Enter key, instead of
literally typing the word Enter.

The positional arguments passed to this script can be used to populate
placeholders in the json values. The placeholders are curly braces with an
optional number inside, where the number indicates which argument to use,
starting from 0. For example, if the we invoke: `key2pane foo bar`, and the
`keys` array is `["echo {1} {2}", "Enter"]`, then the following keys will be
sent to the pane: `echo foo bar`, `Enter`. Python's `str.format` is used under
the hood, so more information can be found in the official documentation.
"""


def make_parser() -> ArgumentParser:
    """Return an ArgumentParser for key2pane.

    Returns:
        An ArgumentParser for key2pane.
    """
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
        help="Specify the tmux window. If not provided, the window specified by"
        "config file will be used. if not set, the current window will"
        " be used.",
    )
    parser.add_argument(
        "-i",
        "--index",
        type=int,
        help="Specify the tmux pane index. If not provided, the value of the "
        "config file will be used. if not set, the current pane its index will "
        "be used.",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Send a C-c before sending the keys",
    )
    parser.add_argument(
        "--logfile",
        default=expanduser("~/.local/state/key2pane/key2pane.log"),
        help="Specify the log file",
    )
    parser.add_argument(
        "--loglevel",
        default="WARNING",
        help="Specify the log level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Do not send the keys, just print the command to stdout instead",
    )
    parser.add_argument(
        "positional",
        nargs="*",
        help=(
            "Positional arguments that will be inserted in '{}' placeholders "
            "in the send keys"
        ),
    )
    return parser


def set_logging(loglevel: str, logfile: str, store_days: int = 7) -> None:
    """Set the root logger to the `loglevel` and add a file handler to
    `logfile`. Logs older than `store_days` will be deleted.

    Args:
        loglevel: The log level.
        logfile: The path to the log file.
        store_days: The number of days to keep the logs.
    """
    makedirs(dirname(logfile), exist_ok=True)

    logging.debug("Initializing logging by printing this message")
    logger: logging.Logger = logging.getLogger()
    logger.setLevel(loglevel)

    formatter: logging.Formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler: TimedRotatingFileHandler = TimedRotatingFileHandler(
        logfile, when="D", interval=1, backupCount=store_days
    )

    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logging.debug("Logging initialized")
