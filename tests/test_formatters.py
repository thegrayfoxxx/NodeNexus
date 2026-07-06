from core.models import MultiServerResult, Result
from plugins.interfaces.formatters import format_multi_server_text


def test_format_multi_server_text():
    results = [
        MultiServerResult(
            host="host1",
            result=Result(stdout="output1\n", stderr="", exit_code=0, duration=0.5, command="ls"),
        ),
        MultiServerResult(
            host="host2",
            result=Result(stdout="output2\n", stderr="", exit_code=0, duration=0.5, command="ls"),
        ),
    ]

    output = format_multi_server_text(results)
    assert "--- host1 ---" in output
    assert "output1" in output
    assert "--- host2 ---" in output
    assert "output2" in output


def test_format_multi_server_text_with_error():
    results = [
        MultiServerResult(host="host1", error="Connection failed"),
        MultiServerResult(
            host="host2",
            result=Result(stdout="output2\n", stderr="", exit_code=0, duration=0.5, command="ls"),
        ),
    ]

    output = format_multi_server_text(results)
    assert "--- host1 ---" in output
    assert "Error: Connection failed" in output
    assert "--- host2 ---" in output
    assert "output2" in output
