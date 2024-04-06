import logging
import sys
from argparse import Namespace
from copy import copy
from pprint import pformat

from key2pane.cli import make_parser, set_logging
from key2pane.settings import Settings, SettingsError, load_config
from key2pane.tmux import Pane, TmuxError


def main() -> int:
    """Entry point for key2pane.

    It catches exceptions defined in this module and logs them as errors.
    Unexpected exceptions are logged as critical and the traceback is included.

    Returns:
        0 if successful, 1 if an error occurred.
    """
    try:
        _main()
    except (SettingsError, TmuxError) as error:
        logging.error(error)
        return 1
    except Exception as error:
        logging.critical(error, exc_info=True)
        return 1
    else:
        return 0


def _main():
    """Entry point for key2pane."""
    args: Namespace = make_parser().parse_args()
    set_logging(args.loglevel, args.logfile)
    logging.debug("Arguments:\n%s", pformat(vars(args)))

    settings: Settings = make_settings(args)
    target_pane: Pane = Pane(settings.session, settings.window, settings.index)
    logging.info("Target pane: %s", target_pane)

    keys: list[str] = settings.get_keys(target_pane.command)
    if args.dry_run:
        logging.warning("Dry run; not sending keys")
        print(*keys)
    else:
        target_pane.send(keys, settings.reset)


def make_settings(args: Namespace) -> Settings:
    """Return a Settings object based on the command line arguments, and the
    config file.

    Args:
        args: the command line arguments.

    Returns:
        the settings.
    """
    active_pane: Pane = Pane.from_active()
    defaults: dict = copy(vars(args))
    defaults.update(active_pane.as_dict())

    config: dict = load_config(args.config)

    overrides: dict = dict(
        session=args.session, window=args.window, index=args.index
    )

    settings: Settings = Settings.from_dicts(defaults, config, overrides)
    logging.debug(
        "Active pane:\n%s\n\nDefaults:\n%s\n\nConfig:\n%s\n\nOverrides:\n%s"
        "\n\nSettings:\n%s\n",
        active_pane,
        pformat(defaults),
        pformat(config),
        pformat(overrides),
        pformat(settings),
    )
    return settings


if __name__ == "__main__":
    sys.exit(main())
