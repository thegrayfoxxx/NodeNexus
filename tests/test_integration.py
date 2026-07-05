import pytest
from nodenexus.core.container import create_container
from nodenexus.core.models import ProtocolType, Server, Command
from nodenexus.core.registry import PluginRegistry


def test_full_workflow():
    """Test complete workflow from container to protocol."""
    container = create_container()
    registry = container.get(PluginRegistry)
    
    # Verify protocol is registered
    protocol_class = registry.get_protocol(ProtocolType.SSH)
    assert protocol_class is not None
    
    # Create protocol instance
    protocol = protocol_class()
    assert protocol is not None
    
    # Verify protocol has required methods
    assert hasattr(protocol, 'connect')
    assert hasattr(protocol, 'execute')
    assert hasattr(protocol, 'close')