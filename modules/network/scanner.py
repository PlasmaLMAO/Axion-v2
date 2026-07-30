import socket

import psutil
from rich.console import Console
from rich.table import Table

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
                    continue  # skip MAC/link-layer addresses
                entries.append({
                    "family": family,
                    "address": addr.address,
                    "netmask": addr.netmask or "-",
                })
            if entries:
                interfaces[iface_name] = entries
        return interfaces

    def display(self) -> None:
        console.print(f"  Hostname:   [#e6e6e6]{self.get_hostname()}[/#e6e6e6]")
        console.print(f"  Primary IP: [#e6e6e6]{self.get_local_ip()}[/#e6e6e6]\n")

        table = Table(title="Network Interfaces", title_style="bold #e6e6e6")
        table.add_column("Interface", style="#999999")
        table.add_column("Family", style="#bfbfbf")
        table.add_column("Address", style="#e6e6e6")
        table.add_column("Netmask", style="#999999")

        for iface_name, entries in self.get_interfaces().items():
            for entry in entries:
                table.add_row(iface_name, entry["family"], entry["address"], entry["netmask"])

        console.print(table)


if __name__ == "__main__":
    NetworkScanner().display()
