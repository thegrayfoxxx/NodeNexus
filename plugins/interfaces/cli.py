import argparse
import json
import sys

from core.container import create_container
from core.exceptions import NodeNexusError
from core.models import Command, ProtocolType, Server
from core.registry import PluginRegistry


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="NodeNexus - Remote Server Management",
        prog="nodenexus",
    )
    parser.add_argument("command", help="Command to execute")
    parser.add_argument("-H", "--host", required=True, help="Server host")
    parser.add_argument("-p", "--port", type=int, default=22, help="SSH port")
    parser.add_argument("-u", "--user", default="root", help="SSH user")
    parser.add_argument("-k", "--key", help="Path to SSH key")
    parser.add_argument("--password", help="SSH password")
    parser.add_argument("-w", "--workdir", help="Working directory on server")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--timeout", type=int, default=30, help="Command timeout")
    return parser.parse_args()


async def run():
    args = parse_args()

    try:
        container = create_container()
        registry = container.get(PluginRegistry)
        protocol_class = registry.get_protocol(ProtocolType.SSH)

        server = Server(
            host=args.host,
            port=args.port,
            user=args.user,
            key_path=args.key,
            password=args.password,
        )
        command = Command(
            text=args.command,
            workdir=args.workdir,
            timeout=args.timeout,
        )

        async with protocol_class() as protocol:
            await protocol.connect(server)
            result = await protocol.execute(command)

        if args.json:
            print(
                json.dumps(
                    {
                        "stdout": result.stdout,
                        "stderr": result.stderr,
                        "exit_code": result.exit_code,
                        "duration": result.duration,
                        "command": result.command,
                    },
                    indent=2,
                )
            )
        else:
            if result.stdout:
                print(result.stdout, end="")
            if result.stderr:
                print(result.stderr, end="", file=sys.stderr)

        sys.exit(result.exit_code)

    except NodeNexusError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)
