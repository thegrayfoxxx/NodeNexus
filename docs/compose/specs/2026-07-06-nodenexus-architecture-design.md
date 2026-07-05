# NodeNexus — Спецификация архитектуры

## [S1] Проблема

Нужен инструмент для удалённого управления серверами с поддержкой множества протоколов (SSH и др.) и интерфейсов (CLI, API). Архитектура должна позволять добавлять новые компоненты без изменения ядра.

## [S2] Требования

- CLI-утилита как основной интерфейс
- API как второй интерфейс (в будущем)
- SSH как основной протокол
- Поддержка от 1 до 100+ серверов
- Фокус на выполнении команд
- Гибкий вывод (потоковый + структурированный)
- Плагинная архитектура для расширяемости
- DI-контейнер (dishka) для управления зависимостями

## [S3] Архитектура

Плагинная архитектура с минимальным ядром и подключаемыми компонентами.

### Структура проекта

```
nodenexus/
├── core/                    
│   ├── __init__.py
│   ├── models.py            # Данные
│   ├── registry.py          # Реестр плагинов
│   ├── container.py         # DI-контейнер (dishka)
│   └── exceptions.py        
├── plugins/                 
│   ├── protocols/           
│   │   ├── __init__.py
│   │   ├── base.py          
│   │   └── ssh.py           
│   └── interfaces/          
│       ├── __init__.py
│       ├── cli.py           
│       └── api.py           
├── main.py                  
├── pyproject.toml
└── tests/
    ├── __init__.py
    ├── test_models.py
    ├── test_registry.py
    └── test_ssh.py
```

## [S4] Модели (core/models.py)

```python
from dataclasses import dataclass
from enum import Enum
from typing import Optional

class ProtocolType(Enum):
    SSH = "ssh"
    # Future: SFTP, RSYNC, etc.

@dataclass(frozen=True)
class Server:
    host: str
    port: int = 22
    user: str = "root"
    key_path: Optional[str] = None
    password: Optional[str] = None

@dataclass(frozen=True)
class Command:
    text: str
    workdir: Optional[str] = None
    timeout: int = 30
    env: dict[str, str] | None = None

@dataclass(frozen=True)
class Result:
    stdout: str
    stderr: str
    exit_code: int
    duration: float
    command: str
```

## [S5] Реестр плагинов (core/registry.py)

```python
from typing import Type, TypeVar
from nodenexus.core.models import ProtocolType

T = TypeVar("T")

class PluginRegistry:
    def __init__(self):
        self._protocols: dict[ProtocolType, Type] = {}
        self._interfaces: dict[str, Type] = {}
    
    def register_protocol(self, protocol_type: ProtocolType, cls: Type) -> None:
        self._protocols[protocol_type] = cls
    
    def get_protocol(self, protocol_type: ProtocolType) -> Type:
        if protocol_type not in self._protocols:
            raise PluginNotFoundError(f"Protocol {protocol_type} not registered")
        return self._protocols[protocol_type]
    
    def register_interface(self, name: str, cls: Type) -> None:
        self._interfaces[name] = cls
    
    def get_interface(self, name: str) -> Type:
        if name not in self._interfaces:
            raise PluginNotFoundError(f"Interface {name} not registered")
        return self._interfaces[name]
```

## [S6] DI-контейнер (core/container.py)

```python
from dishka import make_container, Provider, Scope, provide
from nodenexus.core.registry import PluginRegistry
from nodenexus.plugins.protocols.ssh import SSHProtocol

class AppProvider(Provider):
    scope = Scope.APP
    
    @provide
    def get_registry(self) -> PluginRegistry:
        registry = PluginRegistry()
        registry.register_protocol(ProtocolType.SSH, SSHProtocol)
        return registry

def create_container() -> Container:
    return make_container(AppProvider())
```

## [S7] Абстракция протокола (plugins/protocols/base.py)

```python
from abc import ABC, abstractmethod
from nodenexus.core.models import Server, Command, Result

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
```

## [S8] SSH-плагин (plugins/protocols/ssh.py)

```python
import asyncssh
from nodenexus.core.models import Server, Command, Result
from nodenexus.plugins.protocols.base import BaseProtocol

class SSHProtocol(BaseProtocol):
    def __init__(self):
        self._conn: asyncssh.SSHClientConnection | None = None
    
    async def connect(self, server: Server) -> None:
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
        if not self._conn:
            raise ConnectionError("Not connected")
        
        result = await self._conn.run(
            command.text,
            cwd=command.workdir,
            timeout=command.timeout,
        )
        
        return Result(
            stdout=result.stdout,
            stderr=result.stderr,
            exit_code=result.exit_status,
            duration=0.0,  # TODO: measure
            command=command.text,
        )
    
    async def close(self) -> None:
        if self._conn:
            self._conn.close()
            await self._conn.wait_closed()
```

## [S9] CLI-интерфейс (plugins/interfaces/cli.py)

```python
import argparse
import asyncio
import json
from nodenexus.core.models import Server, Command
from nodenexus.core.container import create_container

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="NodeNexus - Remote Server Management")
    parser.add_argument("command", help="Command to execute")
    parser.add_argument("-H", "--host", required=True, help="Server host")
    parser.add_argument("-p", "--port", type=int, default=22, help="SSH port")
    parser.add_argument("-u", "--user", default="root", help="SSH user")
    parser.add_argument("-k", "--key", help="Path to SSH key")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--timeout", type=int, default=30, help="Command timeout")
    return parser.parse_args()

async def run():
    args = parse_args()
    container = create_container()
    
    server = Server(
        host=args.host,
        port=args.port,
        user=args.user,
        key_path=args.key,
    )
    command = Command(text=args.command, timeout=args.timeout)
    
    # Get protocol from registry and execute
    # ... implementation
    
def main():
    asyncio.run(run())
```

## [S10] Исключения (core/exceptions.py)

```python
class NodeNexusError(Exception):
    pass

class ConnectionError(NodeNexusError):
    pass

class CommandError(NodeNexusError):
    pass

class PluginNotFoundError(NodeNexusError):
    pass
```

## [S11] Зависимости (pyproject.toml)

```toml
[project]
name = "nodenexus"
version = "0.1.0"
description = "Remote server management tool"
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
```

## [S12] Поток данных

```
Пользователь → CLI/API → Container → Registry → Protocol.connect() → Protocol.execute() → Result → CLI/API → Пользователь
```
