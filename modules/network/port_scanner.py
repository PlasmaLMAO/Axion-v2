import sys
from pathlib import Path as _Path

_PROJECT_ROOT = _Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import ipaddress
import socket

from rich.console import Console

from core.theme import THEME, boxless_table, print_centered

console = Console()

COMMON_PORTS = {
    21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP", 53: "DNS",
    80: "HTTP", 110: "POP3", 143: "IMAP", 443: "HTTPS", 445: "SMB",
    3306: "MySQL", 3389: "RDP", 5432: "PostgreSQL", 8080: "HTTP-Alt",
}


class ScopeError(Exception):
    """Raised when a target address is outside the permitted scan scope."""

class PortScanner:

    def validate_target(self, target: str) -> ipaddress.IPv4Address | ipaddress.IPv6Address:
        try:
            resolved = socket.gethostbyname(target)
            addr = ipaddress.ip_address(resolved)
        except socket.gaierror:
            raise ValueError(f"Could not resolve hostname: {target}")

        if not (addr.is_loopback or addr.is_private):
            raise ScopeError(
                f"{target} ({addr}) is outside the permitted scan scope. "
                "Only localhost and private network ranges (RFC 1918) are allowed."
            )
        return addr

    def scan_port(self, ip: str, port: int, timeout: float = 0.5) -> bool:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            result = sock.connect_ex((ip, port))
            return result == 0

    def scan(self, target: str, ports: list[int] | None = None) -> dict[int, bool]:
        addr = self.validate_target(target)
        ports_to_scan = ports if ports is not None else list(COMMON_PORTS.keys())

        results = {}
        for port in ports_to_scan:
            results[port] = self.scan_port(str(addr), port)
        return results

    def display(self, target: str) -> None:
            from rich.console import Group

            try:
                addr = self.validate_target(target)
            except (ScopeError, ValueError) as e:
                print_centered(console, f"[bold {THEME['error']}]Blocked:[/bold {THEME['error']}] {e}")
                return

            print_centered(console, Group(
                f"[bold {THEME['primary']}]Target:[/bold {THEME['primary']}] {target} ({addr}) — within permitted scope.",
                f"[{THEME['faint']}]Only scan networks and hosts you own or have explicit authorization to test.[/{THEME['faint']}]",
            ))

            confirm = console.input("\nProceed with scan? [y/N]: ").strip().lower()
            if confirm != "y":
                print_centered(console, f"[{THEME['faint']}]Scan cancelled.[/{THEME['faint']}]")
                return

            console.print(f"\nScanning {len(COMMON_PORTS)} common ports on {addr}...\n")
            results = self.scan(target)

            table = boxless_table(f"Port Scan Results: {addr}")
            table.add_column("Port", style=THEME["muted"], justify="right")
            table.add_column("Service", style=THEME["secondary"])
            table.add_column("State", style=THEME["primary"])

            for port, is_open in results.items():
                state = f"[bold {THEME['success']}]OPEN[/bold {THEME['success']}]" if is_open else f"[{THEME['faint']}]closed[/{THEME['faint']}]"
                table.add_row(str(port), COMMON_PORTS.get(port, "-"), state)

            print_centered(console, table)

if __name__ == "__main__":
    target = console.input(
        "  Enter a target to scan (localhost/private IPs only, e.g. 127.0.0.1): "
    ).strip()
    if target:
        PortScanner().display(target)
    else:
        console.print("[bold red]No target entered.[/bold red]")
