from plugins.interfaces.tui.app import NodeNexusApp


def test_app_creation():
    app = NodeNexusApp()
    assert app is not None
    assert app.title == "NodeNexus"
