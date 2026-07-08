from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from core.models import Result
from plugins.interfaces.cli import parse_args, run


def test_parse_args_minimal():
    with patch("sys.argv", ["nodenexus", "ls", "-H", "example.com"]):
        args = parse_args()
        assert args.command == "ls"
        assert args.host == "example.com"
        assert args.port == 22
        assert args.user == "root"


def test_parse_args_full():
    with patch(
        "sys.argv",
        [
            "nodenexus",
            "ls -la",
            "-H",
            "example.com",
            "-p",
            "2222",
            "-u",
            "admin",
            "-k",
            "/path/to/key",
            "--json",
            "--timeout",
            "60",
        ],
    ):
        args = parse_args()
        assert args.command == "ls -la"
        assert args.host == "example.com"
        assert args.port == 2222
        assert args.user == "admin"
        assert args.key == "/path/to/key"
        assert args.json is True
        assert args.timeout == 60


@pytest.mark.asyncio
async def test_run_json_output(capsys):
    with patch("sys.argv", ["nodenexus", "ls", "-H", "example.com", "--json"]):
        with patch("plugins.interfaces.cli.create_container") as mock_container:
            mock_registry = MagicMock()
            mock_protocol_class = MagicMock()
            mock_protocol = AsyncMock()
            mock_ctx = AsyncMock()
            mock_ctx.__aenter__.return_value = mock_protocol
            mock_protocol_class.return_value = mock_ctx
            mock_protocol.execute.return_value = Result(
                stdout="file.txt",
                stderr="",
                exit_code=0,
                duration=0.5,
                command="ls",
            )
            mock_registry.get_protocol.return_value = mock_protocol_class
            mock_container.return_value.get.return_value = mock_registry

            with pytest.raises(SystemExit) as exc_info:
                await run()
            assert exc_info.value.code == 0

            captured = capsys.readouterr()
            assert '"stdout": "file.txt"' in captured.out


def test_parse_args_multiple_hosts():
    with patch("sys.argv", ["nodenexus", "ls", "--hosts", "host1,host2,host3"]):
        args = parse_args()
        assert args.hosts == "host1,host2,host3"
        assert args.host is None


@pytest.mark.asyncio
async def test_run_multi_server_json_output(capsys):
    with patch("sys.argv", ["nodenexus", "ls", "--hosts", "host1,host2", "--json"]):
        with patch("plugins.interfaces.cli.create_container") as mock_container:
            mock_registry = MagicMock()
            mock_protocol_class = MagicMock()
            mock_protocol = AsyncMock()
            mock_ctx = AsyncMock()
            mock_ctx.__aenter__.return_value = mock_protocol
            mock_protocol_class.return_value = mock_ctx
            mock_protocol.execute.return_value = Result(
                stdout="file.txt",
                stderr="",
                exit_code=0,
                duration=0.5,
                command="ls",
            )
            mock_registry.get_protocol.return_value = mock_protocol_class
            mock_container.return_value.get.return_value = mock_registry

            with patch("plugins.interfaces.cli.execute_on_servers") as mock_execute:
                from core.models import MultiServerResult

                mock_execute.return_value = [
                    MultiServerResult(
                        host="host1",
                        result=Result(
                            stdout="file.txt",
                            stderr="",
                            exit_code=0,
                            duration=0.5,
                            command="ls",
                        ),
                    ),
                    MultiServerResult(
                        host="host2",
                        result=Result(
                            stdout="file.txt",
                            stderr="",
                            exit_code=0,
                            duration=0.5,
                            command="ls",
                        ),
                    ),
                ]

                with pytest.raises(SystemExit) as exc_info:
                    await run()
                assert exc_info.value.code == 0

                captured = capsys.readouterr()
                assert '"host": "host1"' in captured.out
                assert '"host": "host2"' in captured.out
