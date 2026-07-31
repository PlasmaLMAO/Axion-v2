import sys
from pathlib import Path as _Path

_PROJECT_ROOT = _Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import psutil
from rich.console import Console

from core.theme import THEME, boxless_table, print_centered

console = Console()


class ProcessViewer:

    def get_processes(self) -> list[dict]:
        processes = []
        for proc in psutil.process_iter(
            ["pid", "name", "username", "cpu_percent", "memory_percent"]
        ):
            try:
                info = proc.info
                processes.append(info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return processes

    def display(self, sort_by: str = "cpu_percent", limit: int = 20) -> None:
        processes = self.get_processes()
        processes.sort(key=lambda p: p.get(sort_by) or 0, reverse=True)
        processes = processes[:limit]

        table = boxless_table(f"Running Processes (top {limit} by {sort_by})")
        table.add_column("PID", style=THEME["muted"], justify="right")
        table.add_column("Name", style=THEME["primary"])
        table.add_column("User", style=THEME["secondary"])
        table.add_column("CPU %", style=THEME["muted"], justify="right")
        table.add_column("Memory %", style=THEME["muted"], justify="right")

        for proc in processes:
            table.add_row(
                str(proc.get("pid", "-")),
                proc.get("name") or "-",
                proc.get("username") or "-",
                f"{proc.get('cpu_percent', 0.0):.1f}",
                f"{proc.get('memory_percent', 0.0):.1f}",
            )

        print_centered(console, table)


if __name__ == "__main__":
    ProcessViewer().display()
