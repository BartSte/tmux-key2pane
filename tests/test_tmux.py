from key2pane import tmux


def test_tmux():
    stdout: str = tmux("-c", "echo 'Hello'")
    assert stdout == "Hello", "Make sure tmux is installed"
