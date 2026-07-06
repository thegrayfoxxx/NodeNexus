import argparse
import json
import sys

from core.container import create_container
from core.exceptions import NodeNexusError
from core.models import Command, ProtocolType, Server
from core.registry import PluginRegistry
from plugins.interfaces.formatters import (
    format_multi_server_json,
    format_multi_server_text,
    get_worst_exit_code,
)
from plugins.protocols.multi import execute_on_servers


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="NodeNexus — Управление удалёнными серверами",
        prog="nodenexus",
    )
    parser.add_argument("command", nargs="?", help="Команда для выполнения")

    group = parser.add_mutually_exclusive_group()
    group.add_argument("-H", "--host", help="Хост сервера (один)")
    group.add_argument("--hosts", help="Список хостов через запятую (несколько серверов)")

    parser.add_argument("-p", "--port", type=int, default=22, help="SSH порт")
    parser.add_argument("-u", "--user", default="root", help="SSH пользователь")
    parser.add_argument("-k", "--key", help="Путь к SSH ключу")
    parser.add_argument("--password", help="SSH пароль")
    parser.add_argument("-w", "--workdir", help="Рабочая директория на сервере")
    parser.add_argument("--json", action="store_true", help="Вывод в формате JSON")
    parser.add_argument("--timeout", type=int, default=30, help="Таймаут команды (сек)")
    return parser.parse_args()


def _build_servers(args: argparse.Namespace) -> list[Server]:
    if args.hosts:
        hosts = [h.strip() for h in args.hosts.split(",") if h.strip()]
        return [
            Server(
                host=h,
                port=args.port,
                user=args.user,
                key_path=args.key,
                password=args.password,
            )
            for h in hosts
        ]
    return [
        Server(
            host=args.host,
            port=args.port,
            user=args.user,
            key_path=args.key,
            password=args.password,
        )
    ]


async def run():
    args = parse_args()

    if args.command is None and args.host is None and args.hosts is None:
        from plugins.interfaces.tui.app import NodeNexusApp

        app = NodeNexusApp()
        await app.run_async()
        return

    try:
        container = create_container()
        registry = container.get(PluginRegistry)
        protocol_class = registry.get_protocol(ProtocolType.SSH)

        servers = _build_servers(args)
        command = Command(
            text=args.command,
            workdir=args.workdir,
            timeout=args.timeout,
        )

        if len(servers) == 1:
            async with protocol_class() as protocol:
                await protocol.connect(servers[0])
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
        else:
            results = await execute_on_servers(protocol_class, servers, command)

            if args.json:
                print(json.dumps(format_multi_server_json(results), indent=2))
            else:
                print(format_multi_server_text(results))

            sys.exit(get_worst_exit_code(results))

    except NodeNexusError as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Непредвиденная ошибка: {e}", file=sys.stderr)
        sys.exit(1)
