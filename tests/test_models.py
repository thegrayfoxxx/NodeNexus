from nodenexus.core.models import Server, Command, Result, ProtocolType

def test_server_creation():
    server = Server(host="example.com")
    assert server.host == "example.com"
    assert server.port == 22
    assert server.user == "root"

def test_server_with_options():
    server = Server(
        host="example.com",
        port=2222,
        user="admin",
        key_path="/path/to/key",
    )
    assert server.port == 2222
    assert server.user == "admin"
    assert server.key_path == "/path/to/key"

def test_command_creation():
    command = Command(text="ls -la")
    assert command.text == "ls -la"
    assert command.timeout == 30

def test_command_with_options():
    command = Command(
        text="pwd",
        workdir="/tmp",
        timeout=60,
        env={"HOME": "/root"},
    )
    assert command.workdir == "/tmp"
    assert command.timeout == 60
    assert command.env == {"HOME": "/root"}

def test_result_creation():
    result = Result(
        stdout="file.txt",
        stderr="",
        exit_code=0,
        duration=0.5,
        command="ls",
    )
    assert result.stdout == "file.txt"
    assert result.exit_code == 0

def test_protocol_type_enum():
    assert ProtocolType.SSH.value == "ssh"