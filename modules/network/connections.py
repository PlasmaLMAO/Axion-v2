import sys
from pathlib import Path as _Path

_PROJECT_ROOT = _Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import psutil
from rich.console import Console

from core.theme import THEME, boxless_table, print_centered

console = Console()


class ConnectionMonitor:

    def get_connections(self) -> list[dict[str, str]]:
        connections = []
        for conn in psutil.net_connections(kind="inet"):
            laddr = f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else "-"
            raddr = f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else "-"

            process_name = "-"
            if conn.pid:
                try:
                    process_name = psutil.Process(conn.pid).name()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    process_name = f"PID {conn.pid}"

            connections.append({
                "proto": "TCP" if conn.type == 1 else "UDP",
                "local": laddr,
                "remote": raddr,
                "status": conn.status,
                "pid": str(conn.pid) if conn.pid else "-",
                "process": process_name,
            })
        return connections

    def display(self, filter_status: str | None = None) -> None:
        connections = self.get_connections()

        if filter_status:
            connections = [c for c in connections if c["status"] == filter_status]

        if not connections:
            print_centered(console, f"[{THEME['faint']}]No matching connections found.[/{THEME['faint']}]")
            print_centered(
                console,
                f"[{THEME['faint']}]Note: viewing all processes' connections may require elevated permissions.[/{THEME['faint']}]",
            )
            return

        table = boxless_table("Active Network Connections")
        table.add_column("Proto", style=THEME["muted"])
        table.add_column("Local Address", style=THEME["primary"])
        table.add_column("Remote Address", style=THEME["primary"])
        table.add_column("Status", style=THEME["secondary"])
        table.add_column("PID", style=THEME["muted"], justify="right")
        table.add_column("Process", style=THEME["secondary"])

        for conn in connections:
            table.add_row(
                conn["proto"],
                conn["local"],
                conn["remote"],
                conn["status"],
                conn["pid"],
                conn["process"],
            )

        print_centered(console, table)


if __name__ == "__main__":
    ConnectionMonitor().display()
