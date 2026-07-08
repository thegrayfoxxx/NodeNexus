from core.models import MultiServerResult


def format_multi_server_text(results: list[MultiServerResult]) -> str:
    lines = []
    for r in results:
        lines.append(f"--- {r.host} ---")
        if r.error:
            lines.append(f"Error: {r.error}")
        else:
            if r.result and r.result.stdout:
                lines.append(r.result.stdout.rstrip("\n"))
            if r.result and r.result.stderr:
                lines.append(f"[stderr] {r.result.stderr.rstrip('\n')}")
        lines.append("")
    return "\n".join(lines)


def format_multi_server_json(
    results: list[MultiServerResult],
) -> list[dict[str, str | int | float]]:
    output: list[dict[str, str | int | float]] = []
    for r in results:
        entry: dict[str, str | int | float] = {"host": r.host}
        if r.error:
            entry["error"] = r.error
        else:
            entry["stdout"] = r.result.stdout if r.result else ""
            entry["stderr"] = r.result.stderr if r.result else ""
            entry["exit_code"] = r.result.exit_code if r.result else 1
            entry["duration"] = r.result.duration if r.result else 0.0
        output.append(entry)
    return output


def get_worst_exit_code(results: list[MultiServerResult]) -> int:
    worst = 0
    for r in results:
        if r.error:
            return 1
        if r.result and r.result.exit_code != 0:
            worst = r.result.exit_code
    return worst
