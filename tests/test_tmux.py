from key2pane import tmux


def test_execute():
    stdout: str = tmux.execute("-c", "echo 'Hello'")
    assert stdout == "Hello", "Make sure tmux is installed"


def test_from_active(monkeypatch_tmux):
    pane: tmux.Pane = tmux.Pane.from_active()
    assert str(pane) == "foo:0.0"
    assert pane.command == "bash"


def test_as_dict(monkeypatch_tmux):
    pane: tmux.Pane = tmux.Pane.from_active()
    expected: dict = {
        "session": "foo",
        "window": 0,
        "index": 0,
        "command": "bash",
    }
    actual: dict = pane.as_dict()
    assert actual == expected, actual


def test_send(monkeypatch_tmux):
    pane: tmux.Pane = tmux.Pane.from_active()
    expected: str = "send-keys -t foo:0.0 echo 'Hello' Enter"
    actual: str = pane.send(["echo 'Hello'", "Enter"])
    assert actual == expected, f"{actual=}, {expected=}"
