from core.container import create_container
from core.models import ProtocolType
from core.registry import PluginRegistry


def test_full_workflow():
    container = create_container()
    registry = container.get(PluginRegistry)

    protocol_class = registry.get_protocol(ProtocolType.SSH)
    assert protocol_class is not None

    protocol = protocol_class()
    assert protocol is not None

    assert hasattr(protocol, "connect")
    assert hasattr(protocol, "execute")
    assert hasattr(protocol, "close")


def test_multi_server_workflow():
    container = create_container()
    registry = container.get(PluginRegistry)
    protocol_class = registry.get_protocol(ProtocolType.SSH)
    assert protocol_class is not None
    assert hasattr(protocol_class, "connect")
    assert hasattr(protocol_class, "execute")
    assert hasattr(protocol_class, "close")


def test_multi_server_result_model():
    from core.models import MultiServerResult, Result

    result = MultiServerResult(
        host="example.com",
        result=Result(stdout="output", stderr="", exit_code=0, duration=0.5, command="ls"),
    )
    assert result.host == "example.com"
    assert result.result is not None
    assert result.result.exit_code == 0
