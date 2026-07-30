import psutil
from rich.console import Console
from rich.table import Table

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

        table = Table(
            title=f"Running Processes (top {limit} by {sort_by})",
            title_style="bold #e6e6e6",
        )
        table.add_column("PID", style="#999999", justify="right")
        table.add_column("Name", style="#e6e6e6")
        table.add_column("User", style="#bfbfbf")
        table.add_column("CPU %", style="#999999", justify="right")
        table.add_column("Memory %", style="#999999", justify="right")

        for proc in processes:
            table.add_row(
                str(proc.get("pid", "-")),
                proc.get("name") or "-",
                proc.get("username") or "-",
                f"{proc.get('cpu_percent', 0.0):.1f}",
                f"{proc.get('memory_percent', 0.0):.1f}",
            )

        console.print(table)


if __name__ == "__main__":
    ProcessViewer().display()
