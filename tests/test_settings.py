from key2pane.settings import Settings, load_config
from tests import paths


def test_load_config():
    config: dict = load_config(paths.config)
    assert config.get("session") is None
    assert config.get("window") is None
    assert config.get("index") is None
    assert config.get("reset") is False
    assert config.get("loglevel") == "DEBUG"
    assert config.get("logfile") == "log.log"
    assert isinstance(config.get("actions"), list)


def test_settings_from_dicts():
    active_pane: dict = {"index": 0, "window": 0, "session": "baz"}
    config: dict = load_config(paths.config)
    args: dict = {
        "index": None,
        "window": None,
        "session": "foo",
        "positional": ["foo", "bar"],
    }

    settings: Settings = Settings.from_dicts(active_pane, config, args)

    assert settings.index == 0
    assert settings.window == 0
    assert settings.session == "foo"
    assert settings.actions == config["actions"]
    assert settings.positional == ["foo", "bar"]


def test_settings_get_keys():
    actions: list = [
        {"regex": "foo", "keys": ["a", "b"]},
        {"regex": "bar", "keys": ["c", "d"]},
    ]
    settings: Settings = Settings(0, 0, "foo", False, actions, [""])

    assert settings.regexes == ("foo", "bar")
    assert settings.all_keys == (["a", "b"], ["c", "d"])
    assert settings.get_keys("foo") == ["a", "b"]
