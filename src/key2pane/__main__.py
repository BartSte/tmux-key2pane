import logging
from argparse import Namespace

from key2pane.cli import make_parser, set_logging
from key2pane.settings import load_config, make_settings
from key2pane.tmux import Pane


def main():
    try:
        _main()
    except Exception as error:
        logging.critical(error)


def _main():
    args: Namespace = make_parser().parse_args()
    set_logging(args.loglevel, args.logfile)
    logging.debug("Arguments: %s", args)

    active_pane: Pane = Pane.from_active()
    logging.debug("Active pane: %s", active_pane)

    config: dict = load_config(args.config)
    logging.debug("Config: %s", config)

    settings: Namespace = make_settings(args, active_pane, config)
    logging.debug("Settings: %s", settings)

    destination_pane: Pane = Pane(
        settings.session, settings.window, settings.index
    )
    logging.info("Destination pane: %s", destination_pane)


if __name__ == "__main__":
    main()
