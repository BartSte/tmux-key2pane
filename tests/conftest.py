import logging
import sys

import pytest


@pytest.fixture(scope="module")
def restore_argv():
    old_argv = sys.argv
    yield "restore_argv"
    logging.debug("Restoring sys.argv from %s to %s", sys.argv, old_argv)
    sys.argv = old_argv
