import requests
from rich.console import Console
from rich.table import Table

console = Console()

API_URL = "http://ip-api.com/json/{query}"
REQUEST_TIMEOUT = 5  # seconds; never hang indefinitely on a slow/dead API

FIELDS = [
    ("query", "IP Address"),
    ("country", "Country"),
    ("regionName", "Region"),
    ("city", "City"),
    ("zip", "Postal Code"),
    ("lat", "Latitude"),
    ("lon", "Longitude"),
    ("timezone", "Timezone"),
    ("isp", "ISP"),
    ("org", "Organization"),
    ("as", "ASN"),
]


class IPLookup:
    def lookup(self, ip: str) -> dict | None:
        try:
            response = requests.get(
                API_URL.format(query=ip),
                timeout=REQUEST_TIMEOUT,
            )
            response.raise_for_status()
        except requests.RequestException as e:
            console.print(f"\n[bold red]Request failed:[/bold red] {e}\n")
            return None

        data = response.json()
        if data.get("status") == "fail":
            reason = data.get("message", "unknown error")
            console.print(f"\n[bold red]Lookup failed:[/bold red] {reason}\n")
            return None

        return data

    def display(self, ip: str) -> None:
        data = self.lookup(ip)
        if data is None:
            return

        table = Table(title="IP Intelligence Lookup", title_style="bold #e6e6e6")
        table.add_column("Field", style="#999999")
        table.add_column("Value", style="#e6e6e6")

        for key, label in FIELDS:
            value = data.get(key)
            if value not in (None, ""):
                table.add_row(label, str(value))

        console.print(table)


if __name__ == "__main__":
    ip = console.input(
        "  Enter an IP to look up (leave blank for your own public IP): "
    ).strip()
    IPLookup().display(ip)
