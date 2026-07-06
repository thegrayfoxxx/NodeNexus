from plugins.interfaces.tui.screens import HistoryScreen


def test_history_creation():
    history = HistoryScreen()
    assert history is not None
