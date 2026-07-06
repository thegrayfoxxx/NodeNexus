from dataclasses import dataclass
from enum import Enum


class ProtocolType(Enum):
    SSH = "ssh"


@dataclass(frozen=True)
class Server:
    host: str
    port: int = 22
    user: str = "root"
    key_path: str | None = None
    password: str | None = None


@dataclass(frozen=True)
class Command:
    text: str
    workdir: str | None = None
    timeout: int = 30
    env: dict[str, str] | None = None


@dataclass(frozen=True)
class Result:
    stdout: str
    stderr: str
    exit_code: int
    duration: float
    command: str


@dataclass(frozen=True)
class MultiServerResult:
    host: str
    result: Result | None = None
    error: str | None = None
