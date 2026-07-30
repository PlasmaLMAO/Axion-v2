import platform
from datetime import datetime, timedelta

import psutil
from rich.console import Console
from rich.table import Table

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
        import subprocess

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

    def _render_table(self, title: str, data: dict[str, str]) -> Table:
        table = Table(title=title, show_header=False, title_style="bold #e6e6e6")
        table.add_column("Field", style="#999999")
        table.add_column("Value", style="#e6e6e6")
        for key, value in data.items():
            table.add_row(key, value)
        return table

    def display(self) -> None:
        console.print(self._render_table("Operating System", self.get_os_info()))
        console.print(f"  Uptime: [#e6e6e6]{self.get_uptime()}[/#e6e6e6]\n")
        console.print(self._render_table("CPU", self.get_cpu_info()))
        console.print(self._render_table("Memory", self.get_memory_info()))
        console.print(self._render_table("Disk (/)", self.get_disk_info()))
        gpus = self.get_gpu_info()
        if gpus:
            for i, gpu in enumerate(gpus):
                console.print(self._render_table(f"GPU {i}", gpu))
        else:
            console.print("[dim]No NVIDIA GPU detected (nvidia-smi unavailable).[/dim]\n")

if __name__ == "__main__":
    SystemInfo().display()
