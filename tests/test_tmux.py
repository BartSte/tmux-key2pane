from key2pane import tmux
from tests.helpers import monkeypatch_tmux


def test_tmux():
    stdout: str = tmux.execute("-c", "echo 'Hello'")
    assert stdout == "Hello", "Make sure tmux is installed"


def test_from_active(monkeypatch):
    monkeypatch_tmux(monkeypatch)
    assert str(tmux.Pane.from_active()) == "foo:0:0:bash"
