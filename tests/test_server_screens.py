from plugins.interfaces.tui.screens import ServerFormScreen


def test_server_form_creation():
    form = ServerFormScreen()
    assert form is not None


def test_server_form_with_server():
    server = {"name": "test", "host": "example.com", "port": 22, "user": "admin"}
    form = ServerFormScreen(server=server)
    assert form.server == server
