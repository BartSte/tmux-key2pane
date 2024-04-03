from key2pane import load_config
from tests import paths


def test_load_config():
    config: dict = load_config(paths.config)
    assert config.get("session") is None
    assert config.get("loglevel") == "DEBUG"
