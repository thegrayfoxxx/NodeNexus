import pytest
from nodenexus.plugins.protocols.base import BaseProtocol
from nodenexus.core.models import Server, Command, Result

def test_base_protocol_is_abstract():
    with pytest.raises(TypeError):
        BaseProtocol()

def test_base_protocol_methods():
    class MockProtocol(BaseProtocol):
        async def connect(self, server):
            pass
        
        async def execute(self, command):
            return Result(
                stdout="",
                stderr="",
                exit_code=0,
                duration=0.0,
                command=command.text,
            )
        
        async def close(self):
            pass
    
    protocol = MockProtocol()
    assert hasattr(protocol, 'connect')
    assert hasattr(protocol, 'execute')
    assert hasattr(protocol, 'close')
