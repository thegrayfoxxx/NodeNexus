import asyncssh
from nodenexus.core.models import Server, Command, Result
from nodenexus.core.exceptions import ServerConnectionError
from nodenexus.plugins.protocols.base import BaseProtocol

class SSHProtocol(BaseProtocol):
    """SSH protocol implementation."""
    
    def __init__(self):
        self._conn: asyncssh.SSHClientConnection | None = None
    
    async def connect(self, server: Server) -> None:
        """Connect to server via SSH."""
        connect_kwargs = {
            "host": server.host,
            "port": server.port,
            "username": server.user,
        }
        if server.key_path:
            connect_kwargs["client_keys"] = [server.key_path]
        if server.password:
            connect_kwargs["password"] = server.password
        
        self._conn = await asyncssh.connect(**connect_kwargs)
    
    async def execute(self, command: Command) -> Result:
        """Execute command on server."""
        if not self._conn:
            raise ServerConnectionError("Not connected to server")
        
        result = await self._conn.run(
            command.text,
            cwd=command.workdir,
            timeout=command.timeout,
        )
        
        stdout = result.stdout if isinstance(result.stdout, str) else ""
        stderr = result.stderr if isinstance(result.stderr, str) else ""
        exit_code = result.exit_status if result.exit_status is not None else 0

        return Result(
            stdout=stdout,
            stderr=stderr,
            exit_code=exit_code,
            duration=0.0,
            command=command.text,
        )
    
    async def close(self) -> None:
        """Close SSH connection."""
        if self._conn:
            self._conn.close()
            await self._conn.wait_closed()
