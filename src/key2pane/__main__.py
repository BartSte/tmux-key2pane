import logging
from argparse import Namespace

from key2pane.cli import make_parser, set_logging
from key2pane.settings import Settings, SettingsError, load_config
from key2pane.tmux import Pane, TmuxError


def main() -> int:
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
    target_pane.send(keys, dry_run=args.dry_run)
    logging.info("Sent keys: %s", keys)


if __name__ == "__main__":
    main()
