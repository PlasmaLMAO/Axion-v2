import sys
from pathlib import Path as _Path

_PROJECT_ROOT = _Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import platform
import subprocess
from datetime import datetime, timedelta

import psutil
from rich.console import Console
from rich.align import Align

from core.theme import THEME, boxless_table, print_centered

console = Console()


class SystemInfo:

    def get_os_info(self) -> dict[str, str]:
        return {
            "System": platform.system(),
            "Node Name": platform.node(),
            "Release": platform.release(),
            "Version": platform.version(),
            "Machine": platform.machine(),
            "Python Version": platform.python_version(),
        }

    def get_uptime(self) -> str:
        boot_timestamp = psutil.boot_time()
        boot_time = datetime.fromtimestamp(boot_timestamp)
        uptime = datetime.now() - boot_time
        return str(timedelta(seconds=int(uptime.total_seconds())))

    def get_cpu_info(self) -> dict[str, str]:
        return {
            "Physical Cores": str(psutil.cpu_count(logical=False)),
            "Logical Cores": str(psutil.cpu_count(logical=True)),
            "Current Usage": f"{psutil.cpu_percent(interval=0.5)}%",
        }

    def get_memory_info(self) -> dict[str, str]:
        mem = psutil.virtual_memory()
        return {
            "Total": f"{mem.total / (1024**3):.2f} GB",
            "Used": f"{mem.used / (1024**3):.2f} GB",
            "Available": f"{mem.available / (1024**3):.2f} GB",
            "Usage": f"{mem.percent}%",
        }

    def get_disk_info(self) -> dict[str, str]:
        disk = psutil.disk_usage("/")
        return {
            "Total": f"{disk.total / (1024**3):.2f} GB",
            "Used": f"{disk.used / (1024**3):.2f} GB",
            "Free": f"{disk.free / (1024**3):.2f} GB",
            "Usage": f"{disk.percent}%",
        }

    def get_gpu_info(self) -> list[dict[str, str]]:
        query = "name,driver_version,memory.total,memory.used,temperature.gpu,utilization.gpu"
        try:
            result = subprocess.run(
                ["nvidia-smi", f"--query-gpu={query}", "--format=csv,noheader,nounits"],
                capture_output=True,
                text=True,
                timeout=5,
                check=True,
            )
        except (FileNotFoundError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
            return []

        gpus = []
        for line in result.stdout.strip().splitlines():
            fields = [f.strip() for f in line.split(",")]
            if len(fields) != 6:
                continue
            name, driver, mem_total, mem_used, temp, util = fields
            gpus.append({
                "Name": name,
                "Driver Version": driver,
                "Memory Total": f"{mem_total} MB",
                "Memory Used": f"{mem_used} MB",
                "Temperature": f"{temp} C",
                "Utilization": f"{util}%",
            })
        return gpus

    def _build_table(self, title: str, data: dict):
            """Build (but don't print) a boxless table from a label/value dict."""
            table = boxless_table(title)
            table.add_column("Field", style=THEME["muted"])
            table.add_column("Value", style=THEME["primary"])
            for key, value in data.items():
                table.add_row(key, value)
            return table

    def display(self) -> None:
            """Print all system information sections as one centered block."""
            from rich.console import Group

            renderables = [
                self._build_table("Operating System", self.get_os_info()),
                f"Uptime: [{THEME['primary']}]{self.get_uptime()}[/{THEME['primary']}]",
                "",
                self._build_table("CPU", self.get_cpu_info()),
                self._build_table("Memory", self.get_memory_info()),
                self._build_table("Disk (/)", self.get_disk_info()),
            ]

            gpus = self.get_gpu_info()
            if gpus:
                for i, gpu in enumerate(gpus):
                    renderables.append(self._build_table(f"GPU {i}", gpu))
            else:
                renderables.append(f"[{THEME['faint']}]No NVIDIA GPU detected (nvidia-smi unavailable).[/{THEME['faint']}]")

            print_centered(console, Group(*renderables))

if __name__ == "__main__":
    SystemInfo().display()
