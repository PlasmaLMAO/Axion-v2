import psutil
from rich.console import Console
from rich.table import Table

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
            console.print("[dim]No matching connections found.[/dim]")
            console.print(
                "[dim]Note: viewing all processes' connections may require elevated permissions.[/dim]"
            )
            return

        table = Table(title="Active Network Connections", title_style="bold #e6e6e6")
        table.add_column("Proto", style="#999999")
        table.add_column("Local Address", style="#e6e6e6")
        table.add_column("Remote Address", style="#e6e6e6")
        table.add_column("Status", style="#bfbfbf")
        table.add_column("PID", style="#999999", justify="right")
        table.add_column("Process", style="#bfbfbf")

        for conn in connections:
            table.add_row(
                conn["proto"],
                conn["local"],
                conn["remote"],
                conn["status"],
                conn["pid"],
                conn["process"],
            )

        console.print(table)


if __name__ == "__main__":
    ConnectionMonitor().display()
