import argparse
import json
import sys
from nodenexus.core.models import Server, Command, ProtocolType
from nodenexus.core.container import create_container
from nodenexus.core.registry import PluginRegistry


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
