import pytest
from nodenexus.core.container import create_container
from nodenexus.core.registry import PluginRegistry
from nodenexus.core.models import ProtocolType
from nodenexus.plugins.protocols.ssh import SSHProtocol

def test_container_creation():
    container = create_container()
    assert container is not None

def test_container_provides_registry():
    container = create_container()
    registry = container.get(PluginRegistry)
    assert isinstance(registry, PluginRegistry)

def test_registry_has_ssh_protocol():
    container = create_container()
    registry = container.get(PluginRegistry)
    protocol_class = registry.get_protocol(ProtocolType.SSH)
    assert protocol_class == SSHProtocol
