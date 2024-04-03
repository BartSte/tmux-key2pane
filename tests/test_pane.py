from key2pane import Pane
from tests.helpers import monkeypatch_tmux


def test_from_active(monkeypatch):
    monkeypatch_tmux(monkeypatch)
    assert str(Pane.from_active()) == "foo:0:0:bash"
