def monkeypatch_tmux(monkeypatch):
    def callback(*args):
        display_message: bool = any(x for x in args if x == "display-message")
        list_panes: bool = any(x for x in args if x == "list-panes")

        if display_message:
            return "foo:0:0"
        elif list_panes:
            return "0:bash"
        else:
            raise ValueError(f"Unknown command: {args}")

    monkeypatch.setattr("key2pane.tmux.execute", callback)
