import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from core.exceptions import ServerConnectionError
from core.models import Command, Server
from plugins.protocols.ssh import SSHProtocol


@pytest.fixture
def mock_ssh_connection():
    with patch(
        "plugins.protocols.ssh.asyncssh.connect", new_callable=AsyncMock
    ) as mock_connect:
        mock_conn = AsyncMock()
        mock_connect.return_value = mock_conn
        yield mock_conn, mock_connect


@pytest.mark.asyncio
async def test_ssh_protocol_creation():
    protocol = SSHProtocol()
    assert protocol is not None
    assert protocol._conn is None


@pytest.mark.asyncio
async def test_ssh_connect(mock_ssh_connection):
    mock_conn, mock_connect = mock_ssh_connection
    protocol = SSHProtocol()

    server = Server(host="example.com", user="admin")
    await protocol.connect(server)

    mock_connect.assert_called_once_with(
        host="example.com",
        port=22,
        username="admin",
    )
    assert protocol._conn == mock_conn


@pytest.mark.asyncio
async def test_ssh_connect_with_key(mock_ssh_connection):
    mock_conn, mock_connect = mock_ssh_connection
    protocol = SSHProtocol()

    server = Server(host="example.com", key_path="/path/to/key")
    await protocol.connect(server)

    mock_connect.assert_called_once_with(
        host="example.com",
        port=22,
        username="root",
        client_keys=["/path/to/key"],
    )


@pytest.mark.asyncio
async def test_ssh_execute(mock_ssh_connection):
    mock_conn, mock_connect = mock_ssh_connection
    mock_result = MagicMock()
    mock_result.stdout = "file.txt"
    mock_result.stderr = ""
    mock_result.exit_status = 0
    mock_conn.run.return_value = mock_result

    protocol = SSHProtocol()
    protocol._conn = mock_conn

    command = Command(text="ls")
    result = await protocol.execute(command)

    assert result.stdout == "file.txt"
    assert result.exit_code == 0
    mock_conn.run.assert_called_once_with("ls", cwd=None, timeout=30)


@pytest.mark.asyncio
async def test_ssh_execute_without_connection():
    protocol = SSHProtocol()
    command = Command(text="ls")

    with pytest.raises(ServerConnectionError):
        await protocol.execute(command)


@pytest.mark.asyncio
async def test_ssh_close(mock_ssh_connection):
    mock_conn, mock_connect = mock_ssh_connection
    protocol = SSHProtocol()
    protocol._conn = mock_conn

    await protocol.close()

    mock_conn.close.assert_called_once()
    mock_conn.wait_closed.assert_called_once()
