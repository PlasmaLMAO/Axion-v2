import sys
from pathlib import Path as _Path

_PROJECT_ROOT = _Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import dns.resolver
from rich.console import Console, Group

from core.theme import THEME, boxless_table, print_centered

console = Console()

RECORD_TYPES = ["A", "AAAA", "MX", "TXT", "NS"]


class DNSAnalyzer:

    def get_system_dns_servers(self) -> list[str]:
        try:
            resolver = dns.resolver.Resolver()
            return resolver.nameservers
        except Exception:
            return []

    def query_record(self, domain: str, record_type: str) -> list[str]:
        try:
            answers = dns.resolver.resolve(domain, record_type)
            return [str(answer) for answer in answers]
        except (
            dns.resolver.NXDOMAIN,
            dns.resolver.NoAnswer,
            dns.resolver.NoNameservers,
            dns.exception.Timeout,
        ):
            return []

    def analyze(self, domain: str) -> dict[str, list[str]]:
        results = {}
        for record_type in RECORD_TYPES:
            results[record_type] = self.query_record(domain, record_type)
        return results

    def display(self, domain: str) -> None:
        servers = self.get_system_dns_servers()
        results = self.analyze(domain)

        table = boxless_table(f"DNS Records for {domain}")
        table.add_column("Type", style=THEME["muted"])
        table.add_column("Value(s)", style=THEME["primary"])

        for record_type, values in results.items():
            if values:
                table.add_row(record_type, "\n".join(values))
            else:
                table.add_row(record_type, f"[{THEME['faint']}]none[/{THEME['faint']}]")

        renderables = [f"Analyzing: [{THEME['primary']}]{domain}[/{THEME['primary']}]", ""]
        if servers:
            renderables.append(f"System DNS servers: [{THEME['muted']}]{', '.join(servers)}[/{THEME['muted']}]")
            renderables.append("")
        renderables.append(table)

        print_centered(console, Group(*renderables))


if __name__ == "__main__":
    domain = console.input("  Enter a domain to analyze (e.g. example.com): ").strip()
    if domain:
        DNSAnalyzer().display(domain)
    else:
        console.print("[bold red]No domain entered.[/bold red]")
