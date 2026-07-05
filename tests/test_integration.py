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
