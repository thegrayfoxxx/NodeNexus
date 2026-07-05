import pytest
from nodenexus.core.registry import PluginRegistry
from nodenexus.core.models import ProtocolType
from nodenexus.core.exceptions import PluginNotFoundError


def test_registry_creation():
    registry = PluginRegistry()
    assert registry is not None


def test_register_and_get_protocol():
    registry = PluginRegistry()

    class MockProtocol:
        pass

    registry.register_protocol(ProtocolType.SSH, MockProtocol)
    result = registry.get_protocol(ProtocolType.SSH)
    assert result == MockProtocol


def test_get_unregistered_protocol_raises():
    registry = PluginRegistry()
    with pytest.raises(PluginNotFoundError):
        registry.get_protocol(ProtocolType.SSH)


def test_register_and_get_interface():
    registry = PluginRegistry()

    class MockInterface:
        pass

    registry.register_interface("cli", MockInterface)
    result = registry.get_interface("cli")
    assert result == MockInterface


def test_get_unregistered_interface_raises():
    registry = PluginRegistry()
    with pytest.raises(PluginNotFoundError):
        registry.get_interface("cli")
