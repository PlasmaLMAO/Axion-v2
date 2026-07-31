import sys
import time
from pathlib import Path as _Path

_PROJECT_ROOT = _Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import psutil
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.align import Align

from core.theme import THEME, gradient_lines

console = Console()

REFRESH_SECONDS = 1.0


class Dashboard:

    def _bar(self, percent: float, width: int = 20) -> str:
        filled = int((percent / 100) * width)
        color = THEME["success"] if percent < 60 else THEME["warning"] if percent < 85 else THEME["error"]
        bar = "█" * filled + "░" * (width - filled)
        return f"[{color}]{bar}[/{color}] {percent:5.1f}%"

    def _build_stats_panel(self) -> Panel:
        cpu = psutil.cpu_percent(interval=None)
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage("/")

        table = Table.grid(padding=(0, 1))
        table.add_column(style=THEME["muted"], width=8)
        table.add_column()
        table.add_row("CPU", self._bar(cpu))
        table.add_row("RAM", self._bar(mem.percent))
        table.add_row("Disk", self._bar(disk.percent))

        return Panel(table, title="System", border_style=THEME["border"], padding=(1, 2))

    def _build_connections_panel(self) -> Panel:
        try:
            connections = psutil.net_connections(kind="inet")
        except (psutil.AccessDenied, PermissionError):
            connections = []

        established = sum(1 for c in connections if c.status == "ESTABLISHED")
        listening = sum(1 for c in connections if c.status == "LISTEN")

        table = Table.grid(padding=(0, 1))
        table.add_column(style=THEME["muted"], width=14)
        table.add_column(style=THEME["primary"])
        table.add_row("Established", str(established))
        table.add_row("Listening", str(listening))
        table.add_row("Total", str(len(connections)))

        return Panel(table, title="Connections", border_style=THEME["border"], padding=(1, 2))

    def _build_process_panel(self) -> Panel:
        procs = []
        for p in psutil.process_iter(["name", "cpu_percent"]):
            try:
                procs.append(p.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        procs.sort(key=lambda p: p.get("cpu_percent") or 0, reverse=True)

        table = Table.grid(padding=(0, 1))
        table.add_column(style=THEME["primary"])
        table.add_column(style=THEME["muted"], justify="right")
        for p in procs[:5]:
            table.add_row(p.get("name") or "-", f"{p.get('cpu_percent', 0.0):.1f}%")

        return Panel(table, title="Top Processes", border_style=THEME["border"], padding=(1, 2))

    def _build_header(self) -> Panel:
        title = gradient_lines("AXION V2 — Live Dashboard")
        return Panel(Align.center(title), border_style=THEME["border"])

    def _build_footer(self) -> Panel:
        text = f"[{THEME['faint']}]Refreshing every {REFRESH_SECONDS:.0f}s — Ctrl+C to exit[/{THEME['faint']}]"
        return Panel(Align.center(text), border_style=THEME["border"])

    def _build_layout(self) -> Layout:
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="body"),
            Layout(name="footer", size=3),
        )
        layout["body"].split_row(
            Layout(name="left"),
            Layout(name="right"),
        )
        layout["left"].split_column(
            Layout(name="stats"),
            Layout(name="connections"),
        )
        layout["right"].update(self._build_process_panel())

        layout["header"].update(self._build_header())
        layout["stats"].update(self._build_stats_panel())
        layout["connections"].update(self._build_connections_panel())
        layout["footer"].update(self._build_footer())
        return layout

    def run(self) -> None:
        try:
            with Live(self._build_layout(), console=console, refresh_per_second=1, screen=True) as live:
                while True:
                    time.sleep(REFRESH_SECONDS)
                    live.update(self._build_layout())
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    Dashboard().run()
