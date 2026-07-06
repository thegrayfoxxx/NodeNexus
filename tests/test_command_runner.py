from plugins.interfaces.tui.screens import CommandRunnerScreen


def test_command_runner_creation():
    runner = CommandRunnerScreen()
    assert runner is not None
    assert runner.selected_servers == []
    assert runner.selected_template is None
