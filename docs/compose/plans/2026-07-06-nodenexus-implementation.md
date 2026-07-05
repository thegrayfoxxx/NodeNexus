# NodeNexus Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use compose:subagent (recommended) or compose:execute to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a CLI tool for remote server management with plugin architecture, SSH protocol support, and DI container.

**Architecture:** Plugin-based architecture with minimal core, pluggable protocols and interfaces, and dishka for dependency injection.

**Tech Stack:** Python 3.13, asyncssh, dishka, pytest, pytest-asyncio

---

## Task 1: Project Setup and Dependencies

**Covers:** [S2], [S11]

**Files:**
- Modify: `pyproject.toml`
- Create: `nodenexus/__init__.py`
- Create: `nodenexus/core/__init__.py`
- Create: `nodenexus/core/models.py`
- Create: `nodenexus/core/exceptions.py`
- Create: `tests/__init__.py`
- Create: `tests/test_models.py`

- [ ] **Step 1: Update pyproject.toml with dependencies**

```toml
[project]
name = "nodenexus"
version = "0.1.0"
description = "Remote server management tool"
readme = "README.md"
requires-python = ">=3.13"
dependencies = [
    "asyncssh>=2.14.0",
    "dishka>=1.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-asyncio>=0.21",
]

[project.scripts]
nodenexus = "nodenexus.main:main"
```

- [ ] **Step 2: Create package structure**

```bash
mkdir -p nodenexus/core
mkdir -p nodenexus/plugins/protocols
mkdir -p nodenexus/plugins/interfaces
mkdir -p tests
```

- [ ] **Step 3: Create nodenexus/__init__.py**

```python
"""NodeNexus - Remote server management tool."""
```

- [ ] **Step 4: Create nodenexus/core/__init__.py**

```python
"""Core module for NodeNexus."""
```

- [ ] **Step 5: Create nodenexus/core/exceptions.py**

```python
class NodeNexusError(Exception):
    """Base exception for NodeNexus."""
    pass

class ConnectionError(NodeNexusError):
    """Connection to server failed."""
    pass

class CommandError(NodeNexusError):
    """Command execution failed."""
    pass

class PluginNotFoundError(NodeNexusError):
    """Requested plugin not found in registry."""
    pass
```

- [ ] **Step 6: Create nodenexus/core/models.py**

```python
from dataclasses import dataclass
from enum import Enum
from typing import Optional

class ProtocolType(Enum):
    """Supported protocol types."""
    SSH = "ssh"

@dataclass(frozen=True)
class Server:
    """Server connection details."""
    host: str
    port: int = 22
    user: str = "root"
    key_path: Optional[str] = None
    password: Optional[str] = None

@dataclass(frozen=True)
class Command:
    """Command to execute on server."""
    text: str
    workdir: Optional[str] = None
    timeout: int = 30
    env: dict[str, str] | None = None

@dataclass(frozen=True)
class Result:
    """Command execution result."""
    stdout: str
    stderr: str
    exit_code: int
    duration: float
    command: str
```

- [ ] **Step 7: Create tests/__init__.py**

```python
"""Tests for NodeNexus."""
```

- [ ] **Step 8: Create tests/test_models.py**

```python
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
```

- [ ] **Step 9: Run tests to verify they pass**

Run: `uv run pytest tests/test_models.py -v`
Expected: All tests PASS

- [ ] **Step 10: Commit**

```bash
git add pyproject.toml nodenexus/ tests/
git commit -m "feat: setup project structure with models and exceptions"
```

---

## Task 2: Plugin Registry

**Covers:** [S5]

**Files:**
- Create: `nodenexus/core/registry.py`
- Create: `tests/test_registry.py`

- [ ] **Step 1: Write failing test for registry**

```python
import pytest
from nodenexus.core.registry import PluginRegistry
from nodenexus.core.models import ProtocolType
from nodenexus.core.exceptions import PluginNotFoundError

def test_registry_creation():
    registry = PluginRegistry()
    assert registry is not None

def test_register_and_get_protocol():
    registry = PluginRegistry()
    
    class MockProtocol:
        pass
    
    registry.register_protocol(ProtocolType.SSH, MockProtocol)
    result = registry.get_protocol(ProtocolType.SSH)
    assert result == MockProtocol

def test_get_unregistered_protocol_raises():
    registry = PluginRegistry()
    with pytest.raises(PluginNotFoundError):
        registry.get_protocol(ProtocolType.SSH)

def test_register_and_get_interface():
    registry = PluginRegistry()
    
    class MockInterface:
        pass
    
    registry.register_interface("cli", MockInterface)
    result = registry.get_interface("cli")
    assert result == MockInterface

def test_get_unregistered_interface_raises():
    registry = PluginRegistry()
    with pytest.raises(PluginNotFoundError):
        registry.get_interface("cli")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_registry.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'nodenexus.core.registry'"

- [ ] **Step 3: Write minimal implementation**

```python
from typing import Type, TypeVar
from nodenexus.core.models import ProtocolType
from nodenexus.core.exceptions import PluginNotFoundError

T = TypeVar("T")

class PluginRegistry:
    """Registry for plugins (protocols and interfaces)."""
    
    def __init__(self):
        self._protocols: dict[ProtocolType, Type] = {}
        self._interfaces: dict[str, Type] = {}
    
    def register_protocol(self, protocol_type: ProtocolType, cls: Type) -> None:
        """Register a protocol implementation."""
        self._protocols[protocol_type] = cls
    
    def get_protocol(self, protocol_type: ProtocolType) -> Type:
        """Get a registered protocol implementation."""
        if protocol_type not in self._protocols:
            raise PluginNotFoundError(f"Protocol {protocol_type} not registered")
        return self._protocols[protocol_type]
    
    def register_interface(self, name: str, cls: Type) -> None:
        """Register an interface implementation."""
        self._interfaces[name] = cls
    
    def get_interface(self, name: str) -> Type:
        """Get a registered interface implementation."""
        if name not in self._interfaces:
            raise PluginNotFoundError(f"Interface {name} not registered")
        return self._interfaces[name]
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_registry.py -v`
Expected: All tests PASS

- [ ] **Step 5: Commit**

```bash
git add nodenexus/core/registry.py tests/test_registry.py
git commit -m "feat: add plugin registry"
```

---

## Task 3: Base Protocol Abstraction

**Covers:** [S7]

**Files:**
- Create: `nodenexus/plugins/__init__.py`
- Create: `nodenexus/plugins/protocols/__init__.py`
- Create: `nodenexus/plugins/protocols/base.py`
- Create: `tests/test_base_protocol.py`

- [ ] **Step 1: Write failing test for base protocol**

```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_base_protocol.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'nodenexus.plugins'"

- [ ] **Step 3: Write minimal implementation**

```python
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_base_protocol.py -v`
Expected: All tests PASS

- [ ] **Step 5: Commit**

```bash
git add nodenexus/plugins/ tests/test_base_protocol.py
git commit -m "feat: add base protocol abstraction"
```

---

## Task 4: SSH Protocol Implementation

**Covers:** [S8]

**Files:**
- Create: `nodenexus/plugins/protocols/ssh.py`
- Create: `tests/test_ssh.py`

- [ ] **Step 1: Write failing test for SSH protocol**

```python
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from nodenexus.plugins.protocols.ssh import SSHProtocol
from nodenexus.core.models import Server, Command, Result

@pytest.fixture
def mock_ssh_connection():
    with patch('nodenexus.plugins.protocols.ssh.asyncssh.connect') as mock_connect:
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
    
    with pytest.raises(ConnectionError):
        await protocol.execute(command)

@pytest.mark.asyncio
async def test_ssh_close(mock_ssh_connection):
    mock_conn, mock_connect = mock_ssh_connection
    protocol = SSHProtocol()
    protocol._conn = mock_conn
    
    await protocol.close()
    
    mock_conn.close.assert_called_once()
    mock_conn.wait_closed.assert_called_once()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_ssh.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'nodenexus.plugins.protocols.ssh'"

- [ ] **Step 3: Write minimal implementation**

```python
import asyncssh
from nodenexus.core.models import Server, Command, Result
from nodenexus.core.exceptions import ConnectionError
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
            raise ConnectionError("Not connected to server")
        
        result = await self._conn.run(
            command.text,
            cwd=command.workdir,
            timeout=command.timeout,
        )
        
        return Result(
            stdout=result.stdout,
            stderr=result.stderr,
            exit_code=result.exit_status,
            duration=0.0,
            command=command.text,
        )
    
    async def close(self) -> None:
        """Close SSH connection."""
        if self._conn:
            self._conn.close()
            await self._conn.wait_closed()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_ssh.py -v`
Expected: All tests PASS

- [ ] **Step 5: Commit**

```bash
git add nodenexus/plugins/protocols/ssh.py tests/test_ssh.py
git commit -m "feat: add SSH protocol implementation"
```

---

## Task 5: DI Container Setup

**Covers:** [S6]

**Files:**
- Create: `nodenexus/core/container.py`
- Create: `tests/test_container.py`

- [ ] **Step 1: Write failing test for container**

```python
import pytest
from nodenexus.core.container import create_container
from nodenexus.core.registry import PluginRegistry
from nodenexus.core.models import ProtocolType
from nodenexus.plugins.protocols.ssh import SSHProtocol

def test_container_creation():
    container = create_container()
    assert container is not None

def test_container_provides_registry():
    container = create_container()
    registry = container.get(PluginRegistry)
    assert isinstance(registry, PluginRegistry)

def test_registry_has_ssh_protocol():
    container = create_container()
    registry = container.get(PluginRegistry)
    protocol_class = registry.get_protocol(ProtocolType.SSH)
    assert protocol_class == SSHProtocol
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_container.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'nodenexus.core.container'"

- [ ] **Step 3: Write minimal implementation**

```python
from dishka import make_container, Provider, Scope, provide
from nodenexus.core.registry import PluginRegistry
from nodenexus.core.models import ProtocolType
from nodenexus.plugins.protocols.ssh import SSHProtocol

class AppProvider(Provider):
    """Application-level dependency provider."""
    scope = Scope.APP
    
    @provide
    def get_registry(self) -> PluginRegistry:
        """Create and configure plugin registry."""
        registry = PluginRegistry()
        registry.register_protocol(ProtocolType.SSH, SSHProtocol)
        return registry

def create_container():
    """Create the DI container."""
    return make_container(AppProvider())
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_container.py -v`
Expected: All tests PASS

- [ ] **Step 5: Commit**

```bash
git add nodenexus/core/container.py tests/test_container.py
git commit -m "feat: add DI container with dishka"
```

---

## Task 6: CLI Interface

**Covers:** [S9]

**Files:**
- Create: `nodenexus/plugins/__init__.py`
- Create: `nodenexus/plugins/interfaces/__init__.py`
- Create: `nodenexus/plugins/interfaces/cli.py`
- Create: `nodenexus/main.py`
- Create: `tests/test_cli.py`

- [ ] **Step 1: Write failing test for CLI**

```python
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from nodenexus.plugins.interfaces.cli import parse_args, run
from nodenexus.core.models import Result

def test_parse_args_minimal():
    with patch('sys.argv', ['nodenexus', 'ls', '-H', 'example.com']):
        args = parse_args()
        assert args.command == 'ls'
        assert args.host == 'example.com'
        assert args.port == 22
        assert args.user == 'root'

def test_parse_args_full():
    with patch('sys.argv', [
        'nodenexus', 'ls -la',
        '-H', 'example.com',
        '-p', '2222',
        '-u', 'admin',
        '-k', '/path/to/key',
        '--json',
        '--timeout', '60',
    ]):
        args = parse_args()
        assert args.command == 'ls -la'
        assert args.host == 'example.com'
        assert args.port == 2222
        assert args.user == 'admin'
        assert args.key == '/path/to/key'
        assert args.json is True
        assert args.timeout == 60

@pytest.mark.asyncio
async def test_run_json_output(capsys):
    with patch('sys.argv', ['nodenexus', 'ls', '-H', 'example.com', '--json']):
        with patch('nodenexus.plugins.interfaces.cli.create_container') as mock_container:
            mock_registry = MagicMock()
            mock_protocol_class = AsyncMock()
            mock_protocol = AsyncMock()
            mock_protocol.execute.return_value = Result(
                stdout="file.txt",
                stderr="",
                exit_code=0,
                duration=0.5,
                command="ls",
            )
            mock_protocol_class.return_value = mock_protocol
            mock_registry.get_protocol.return_value = mock_protocol_class
            mock_container.return_value.get.return_value = mock_registry
            
            await run()
            
            captured = capsys.readouterr()
            assert '"stdout": "file.txt"' in captured.out
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_cli.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'nodenexus.plugins.interfaces.cli'"

- [ ] **Step 3: Write minimal implementation**

```python
import argparse
import asyncio
import json
import sys
from nodenexus.core.models import Server, Command
from nodenexus.core.container import create_container

def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="NodeNexus - Remote Server Management",
        prog="nodenexus",
    )
    parser.add_argument("command", help="Command to execute")
    parser.add_argument("-H", "--host", required=True, help="Server host")
    parser.add_argument("-p", "--port", type=int, default=22, help="SSH port")
    parser.add_argument("-u", "--user", default="root", help="SSH user")
    parser.add_argument("-k", "--key", help="Path to SSH key")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--timeout", type=int, default=30, help="Command timeout")
    return parser.parse_args()

async def run():
    """Execute command on remote server."""
    args = parse_args()
    container = create_container()
    registry = container.get(PluginRegistry)
    
    from nodenexus.core.models import ProtocolType
    protocol_class = registry.get_protocol(ProtocolType.SSH)
    
    server = Server(
        host=args.host,
        port=args.port,
        user=args.user,
        key_path=args.key,
    )
    command = Command(text=args.command, timeout=args.timeout)
    
    async with protocol_class() as protocol:
        await protocol.connect(server)
        result = await protocol.execute(command)
    
    if args.json:
        print(json.dumps({
            "stdout": result.stdout,
            "stderr": result.stderr,
            "exit_code": result.exit_code,
            "duration": result.duration,
            "command": result.command,
        }, indent=2))
    else:
        if result.stdout:
            print(result.stdout, end="")
        if result.stderr:
            print(result.stderr, end="", file=sys.stderr)
    
    sys.exit(result.exit_code)
```

- [ ] **Step 4: Update nodenexus/main.py**

```python
import asyncio
from nodenexus.plugins.interfaces.cli import run

def main():
    """Main entry point."""
    asyncio.run(run())

if __name__ == "__main__":
    main()
```

- [ ] **Step 5: Run test to verify it passes**

Run: `uv run pytest tests/test_cli.py -v`
Expected: All tests PASS

- [ ] **Step 6: Commit**

```bash
git add nodenexus/plugins/interfaces/cli.py nodenexus/main.py tests/test_cli.py
git commit -m "feat: add CLI interface"
```

---

## Task 7: Integration Test

**Covers:** [S12]

**Files:**
- Create: `tests/test_integration.py`

- [ ] **Step 1: Write integration test**

```python
import pytest
from nodenexus.core.container import create_container
from nodenexus.core.models import ProtocolType, Server, Command

def test_full_workflow():
    """Test complete workflow from container to protocol."""
    container = create_container()
    registry = container.get(PluginRegistry)
    
    # Verify protocol is registered
    protocol_class = registry.get_protocol(ProtocolType.SSH)
    assert protocol_class is not None
    
    # Create protocol instance
    protocol = protocol_class()
    assert protocol is not None
    
    # Verify protocol has required methods
    assert hasattr(protocol, 'connect')
    assert hasattr(protocol, 'execute')
    assert hasattr(protocol, 'close')
```

- [ ] **Step 2: Run test to verify it passes**

Run: `uv run pytest tests/test_integration.py -v`
Expected: All tests PASS

- [ ] **Step 3: Commit**

```bash
git add tests/test_integration.py
git commit -m "test: add integration test"
```

---

## Task 8: Final Verification

**Covers:** All sections

**Files:** None

- [ ] **Step 1: Run all tests**

Run: `uv run pytest -v`
Expected: All tests PASS

- [ ] **Step 2: Run type check**

Run: `uv run mypy nodenexus/`
Expected: No type errors (if mypy installed)

- [ ] **Step 3: Run linter**

Run: `uv run ruff check nodenexus/`
Expected: No linting errors

- [ ] **Step 4: Test CLI manually**

Run: `uv run python -m nodenexus.main --help`
Expected: Help message displayed

- [ ] **Step 5: Final commit**

```bash
git add -A
git commit -m "chore: final verification and cleanup"
```
