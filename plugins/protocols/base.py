from abc import ABC, abstractmethod

from core.models import Command, Result, Server


class BaseProtocol(ABC):
    @abstractmethod
    async def connect(self, server: Server) -> None: ...

    @abstractmethod
    async def execute(self, command: Command) -> Result: ...

    @abstractmethod
    async def close(self) -> None: ...

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.close()
