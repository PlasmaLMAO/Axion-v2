import ipaddress
import socket

from rich.console import Console
from rich.table import Table

console = Console()

COMMON_PORTS = {
    21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP", 53: "DNS",
    80: "HTTP", 110: "POP3", 143: "IMAP", 443: "HTTPS", 445: "SMB",
    3306: "MySQL", 3389: "RDP", 5432: "PostgreSQL", 8080: "HTTP-Alt",
}


class ScopeError(Exception):
    """Raised when a target address is outside the permitted scan scope."""


class PortScanner:
    """TCP connect-scan limited to localhost and private network ranges."""

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
        try:
            addr = self.validate_target(target)
        except (ScopeError, ValueError) as e:
            console.print(f"\n[bold red]Blocked:[/bold red] {e}\n")
            return

        console.print(
            f"\n[bold #e6e6e6]Target:[/bold #e6e6e6] {target} ({addr}) — within permitted scope."
        )
        console.print(
            "[dim]Only scan networks and hosts you own or have explicit authorization to test.[/dim]"
        )
        confirm = console.input("\nProceed with scan? [y/N]: ").strip().lower()
        if confirm != "y":
            console.print("[dim]Scan cancelled.[/dim]")
            return

        console.print(f"\nScanning {len(COMMON_PORTS)} common ports on {addr}...\n")
        results = self.scan(target)

        table = Table(title=f"Port Scan Results: {addr}", title_style="bold #e6e6e6")
        table.add_column("Port", style="#999999", justify="right")
        table.add_column("Service", style="#bfbfbf")
        table.add_column("State", style="#e6e6e6")

        for port, is_open in results.items():
            state = "[bold #e6e6e6]OPEN[/bold #e6e6e6]" if is_open else "[dim]closed[/dim]"
            table.add_row(str(port), COMMON_PORTS.get(port, "-"), state)

        console.print(table)


if __name__ == "__main__":
    target = console.input(
        "  Enter a target to scan (localhost/private IPs only, e.g. 127.0.0.1): "
    ).strip()
    if target:
        PortScanner().display(target)
    else:
        console.print("[bold red]No target entered.[/bold red]")
