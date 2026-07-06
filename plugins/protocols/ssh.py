import asyncssh

from core.exceptions import CommandError, ServerConnectionError
from core.models import Command, Result, Server
from plugins.protocols.base import BaseProtocol


class SSHProtocol(BaseProtocol):
    def __init__(self):
        self._conn: asyncssh.SSHClientConnection | None = None

    async def connect(self, server: Server) -> None:
        connect_kwargs = {
            "host": server.host,
            "port": server.port,
            "username": server.user,
            "known_hosts": None,
        }
        if server.key_path:
            connect_kwargs["client_keys"] = [server.key_path]
        if server.password:
            connect_kwargs["password"] = server.password

        try:
            self._conn = await asyncssh.connect(**connect_kwargs)
        except (asyncssh.Error, OSError) as e:
            raise ServerConnectionError(f"Ошибка подключения: {e}") from e

    async def execute(self, command: Command) -> Result:
        if not self._conn:
            raise ServerConnectionError("Нет подключения к серверу")

        cmd = command.text
        if command.workdir:
            cmd = f"cd {command.workdir} && {cmd}"

        try:
            result = await self._conn.run(
                cmd,
                timeout=command.timeout,
            )
        except asyncssh.TimeoutError as e:
            raise CommandError(f"Команда превысила таймаут {command.timeout}с") from e
        except asyncssh.Error as e:
            raise CommandError(f"Ошибка выполнения команды: {e}") from e

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
        if self._conn:
            self._conn.close()
            await self._conn.wait_closed()
