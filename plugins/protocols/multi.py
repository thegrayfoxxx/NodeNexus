import asyncio

from core.models import Command, MultiServerResult, Server
from plugins.protocols.base import BaseProtocol


async def execute_on_servers(
    protocol_class: type[BaseProtocol],
    servers: list[Server],
    command: Command,
) -> list[MultiServerResult]:
    async def _run_single(server: Server) -> MultiServerResult:
        try:
            async with protocol_class() as protocol:
                await protocol.connect(server)
                result = await protocol.execute(command)
                return MultiServerResult(host=server.host, result=result)
        except Exception as e:
            return MultiServerResult(host=server.host, error=str(e))

    return await asyncio.gather(*[_run_single(s) for s in servers])
