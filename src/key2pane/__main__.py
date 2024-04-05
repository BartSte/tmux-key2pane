import logging
import sys
from argparse import Namespace

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
    logging.debug("Arguments: %s", args)

    active_pane: Pane = Pane.from_active()
    logging.debug("Active pane: %s", active_pane)

    config: dict = load_config(args.config)
    logging.debug("Config: %s", config)

    settings: Settings = Settings.from_dicts(
        active_pane.as_dict(), config, vars(args)
    )
    logging.debug("Settings: %s", settings)

    target_pane: Pane = Pane(settings.session, settings.window, settings.index)
    logging.info("Target pane: %s", target_pane)

    keys: list[str] = settings.get_keys(target_pane.command)
    if args.dry_run:
        logging.warning("Dry run; not sending keys")
        print(*keys)
    else:
        logging.info("Sent keys: %s", keys)
        target_pane.send(keys)


if __name__ == "__main__":
    sys.exit(main())
