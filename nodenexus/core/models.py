from dataclasses import dataclass
from enum import Enum

class ProtocolType(Enum):
    """Supported protocol types."""
    SSH = "ssh"

@dataclass(frozen=True)
class Server:
    """Server connection details."""
    host: str
    port: int = 22
    user: str = "root"
    key_path: str | None = None
    password: str | None = None

@dataclass(frozen=True)
class Command:
    """Command to execute on server."""
    text: str
    workdir: str | None = None
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