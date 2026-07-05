from abc import ABC, abstractmethod
from nodenexus.core.models import Server, Command, Result

class BaseProtocol(ABC):
    """Abstract base class for protocols."""
    
    @abstractmethod
    async def connect(self, server: Server) -> None:
        """Connect to a server."""
        ...
    
    @abstractmethod
    async def execute(self, command: Command) -> Result:
        """Execute a command on the server."""
        ...
    
    @abstractmethod
    async def close(self) -> None:
        """Close the connection."""
        ...
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, *args):
        await self.close()
