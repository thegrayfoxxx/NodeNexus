from unittest.mock import AsyncMock, MagicMock

import pytest

from core.exceptions import ServerConnectionError
from core.models import Command, Server
from plugins.protocols.multi import execute_on_servers


@pytest.mark.asyncio
async def test_execute_on_servers_success():
    mock_protocol_class = MagicMock()
    mock_protocol = AsyncMock()
    mock_ctx = AsyncMock()
    mock_ctx.__aenter__.return_value = mock_protocol
    mock_protocol_class.return_value = mock_ctx
    mock_protocol.execute.return_value = MagicMock(
        stdout="output", stderr="", exit_code=0, duration=0.5, command="ls"
    )

    servers = [
        Server(host="host1"),
        Server(host="host2"),
    ]

    results = await execute_on_servers(mock_protocol_class, servers, Command(text="ls"))

    assert len(results) == 2
    assert results[0].host == "host1"
    assert results[0].result is not None
    assert results[0].result.exit_code == 0
    assert results[1].host == "host2"


@pytest.mark.asyncio
async def test_execute_on_servers_partial_failure():
    mock_protocol_class = MagicMock()
    mock_protocol = AsyncMock()
    mock_ctx = AsyncMock()
    mock_ctx.__aenter__.return_value = mock_protocol

    call_count = 0

    async def mock_execute(cmd):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise ServerConnectionError("Connection failed")
        return MagicMock(stdout="output", stderr="", exit_code=0, duration=0.5, command="ls")

    mock_protocol.execute = mock_execute
    mock_protocol_class.return_value = mock_ctx

    servers = [
        Server(host="host1"),
        Server(host="host2"),
    ]

    results = await execute_on_servers(mock_protocol_class, servers, Command(text="ls"))

    assert len(results) == 2
    assert results[0].host == "host1"
    assert results[0].error == "Connection failed"
    assert results[1].host == "host2"
    assert results[1].result is not None
    assert results[1].result.exit_code == 0
