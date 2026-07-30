import dns.resolver
from rich.console import Console
from rich.table import Table

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
        console.print(f"\n  Analyzing: [#e6e6e6]{domain}[/#e6e6e6]\n")

        servers = self.get_system_dns_servers()
        if servers:
            console.print(f"  System DNS servers: [#999999]{', '.join(servers)}[/#999999]\n")

        results = self.analyze(domain)

        table = Table(title=f"DNS Records for {domain}", title_style="bold #e6e6e6")
        table.add_column("Type", style="#999999")
        table.add_column("Value(s)", style="#e6e6e6")

        for record_type, values in results.items():
            if values:
                table.add_row(record_type, "\n".join(values))
            else:
                table.add_row(record_type, "[dim]none[/dim]")

        console.print(table)


if __name__ == "__main__":
    domain = console.input("  Enter a domain to analyze (e.g. example.com): ").strip()
    if domain:
        DNSAnalyzer().display(domain)
    else:
        console.print("[bold red]No domain entered.[/bold red]")
