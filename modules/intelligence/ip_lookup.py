import sys
from pathlib import Path as _Path

_PROJECT_ROOT = _Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import requests
from rich.console import Console

from core.theme import THEME, boxless_table, print_centered

console = Console()

API_URL = "http://ip-api.com/json/{query}"
REQUEST_TIMEOUT = 5

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
            print_centered(console, f"[bold {THEME['error']}]Request failed:[/bold {THEME['error']}] {e}")
            return None

        data = response.json()
        if data.get("status") == "fail":
            reason = data.get("message", "unknown error")
            print_centered(console, f"[bold {THEME['error']}]Lookup failed:[/bold {THEME['error']}] {reason}")
            return None

        return data

    def display(self, ip: str) -> None:
        data = self.lookup(ip)
        if data is None:
            return

        table = boxless_table("IP Intelligence Lookup")
        table.add_column("Field", style=THEME["muted"])
        table.add_column("Value", style=THEME["primary"])

        for key, label in FIELDS:
            value = data.get(key)
            if value not in (None, ""):
                table.add_row(label, str(value))

        print_centered(console, table)


if __name__ == "__main__":
    ip = console.input(
        "  Enter an IP to look up (leave blank for your own public IP): "
    ).strip()
    IPLookup().display(ip)
