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