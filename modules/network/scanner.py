import sys
from pathlib import Path as _Path

_PROJECT_ROOT = _Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import socket

import psutil
from rich.console import Console, Group
from rich.align import Align

from core.theme import THEME, boxless_table, print_centered

console = Console()


class NetworkScanner:

    def get_hostname(self) -> str:
        return socket.gethostname()

    def get_local_ip(self) -> str:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                return s.getsockname()[0]
        except OSError:
            return "Unavailable"

    def get_interfaces(self) -> dict[str, list[dict[str, str]]]:
        interfaces = {}
        for iface_name, addrs in psutil.net_if_addrs().items():
            entries = []
            for addr in addrs:
                if addr.family == socket.AF_INET:
                    family = "IPv4"
                elif addr.family == socket.AF_INET6:
                    family = "IPv6"
                else:
                    continue
                entries.append({
                    "family": family,
                    "address": addr.address,
                    "netmask": addr.netmask or "-",
                })
            if entries:
                interfaces[iface_name] = entries
        return interfaces

    def display(self) -> None:
        table = boxless_table("Network Interfaces")
        table.add_column("Interface", style=THEME["muted"])
        table.add_column("Family", style=THEME["secondary"])
        table.add_column("Address", style=THEME["primary"])
        table.add_column("Netmask", style=THEME["muted"])

        for iface_name, entries in self.get_interfaces().items():
            for entry in entries:
                table.add_row(iface_name, entry["family"], entry["address"], entry["netmask"])

        renderables = [
            f"Hostname:   [{THEME['primary']}]{self.get_hostname()}[/{THEME['primary']}]",
            f"Primary IP: [{THEME['primary']}]{self.get_local_ip()}[/{THEME['primary']}]",
            "",
            table,
        ]

        print_centered(console, Group(*renderables))


if __name__ == "__main__":
    NetworkScanner().display()
