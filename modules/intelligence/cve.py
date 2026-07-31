import sys
from pathlib import Path as _Path

_PROJECT_ROOT = _Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import requests
from rich.console import Console, Group

from core.theme import THEME, boxless_table, print_centered

console = Console()

NVD_API_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0"
REQUEST_TIMEOUT = 10
RESULTS_LIMIT = 10

SEVERITY_COLORS = {
    "CRITICAL": "error",
    "HIGH": "error",
    "MEDIUM": "warning",
    "LOW": "success",
}


class CVELookup:
    """Looks up CVE details by ID or keyword search."""

    def lookup_by_id(self, cve_id: str) -> dict | None:
        try:
            response = requests.get(
                NVD_API_URL,
                params={"cveId": cve_id.upper()},
                timeout=REQUEST_TIMEOUT,
            )
            response.raise_for_status()
        except requests.RequestException as e:
            print_centered(console, f"[bold {THEME['error']}]Request failed:[/bold {THEME['error']}] {e}")
            return None

        data = response.json()
        vulnerabilities = data.get("vulnerabilities", [])
        if not vulnerabilities:
            print_centered(console, f"[bold {THEME['error']}]No results found for:[/bold {THEME['error']}] {cve_id}")
            return None

        return vulnerabilities[0]["cve"]

    def search_by_keyword(self, keyword: str) -> list[dict]:
        try:
            response = requests.get(
                NVD_API_URL,
                params={"keywordSearch": keyword, "resultsPerPage": RESULTS_LIMIT},
                timeout=REQUEST_TIMEOUT,
            )
            response.raise_for_status()
        except requests.RequestException as e:
            print_centered(console, f"[bold {THEME['error']}]Request failed:[/bold {THEME['error']}] {e}")
            return []

        data = response.json()
        return [v["cve"] for v in data.get("vulnerabilities", [])]

    def _extract_summary(self, cve: dict) -> dict[str, str]:
        cve_id = cve.get("id", "-")

        descriptions = cve.get("descriptions", [])
        description = next(
            (d["value"] for d in descriptions if d.get("lang") == "en"),
            "No description available.",
        )

        metrics = cve.get("metrics", {})
        severity = "Unknown"
        score = "-"
        for metric_key in ("cvssMetricV31", "cvssMetricV30", "cvssMetricV2"):
            if metric_key in metrics and metrics[metric_key]:
                metric_data = metrics[metric_key][0]
                cvss_data = metric_data.get("cvssData", {})
                severity = metric_data.get("baseSeverity", cvss_data.get("baseSeverity", "Unknown"))
                score = str(cvss_data.get("baseScore", "-"))
                break

        return {
            "id": cve_id,
            "severity": severity,
            "score": score,
            "description": description,
        }

    def _severity_style(self, severity: str) -> str:
        return THEME[SEVERITY_COLORS.get(severity.upper(), "muted")]

    def display_by_id(self, cve_id: str) -> None:
        cve = self.lookup_by_id(cve_id)
        if cve is None:
            return

        summary = self._extract_summary(cve)
        sev_color = self._severity_style(summary["severity"])

        table = boxless_table(f"CVE Details: {summary['id']}")
        table.add_column("Field", style=THEME["muted"])
        table.add_column("Value", style=THEME["primary"])
        table.add_row("Severity", f"[bold {sev_color}]{summary['severity']}[/bold {sev_color}]")
        table.add_row("CVSS Score", summary["score"])
        table.add_row("Published", cve.get("published", "-"))

        renderables = [
            table,
            "",
            f"[bold {THEME['primary']}]Description:[/bold {THEME['primary']}]",
            summary["description"],
        ]
        print_centered(console, Group(*renderables))

    def display_by_keyword(self, keyword: str) -> None:
        results = self.search_by_keyword(keyword)
        if not results:
            print_centered(console, f"[{THEME['faint']}]No CVEs found matching '{keyword}'.[/{THEME['faint']}]")
            return

        table = boxless_table(f"CVE Search Results for '{keyword}' (showing up to {RESULTS_LIMIT})")
        table.add_column("CVE ID", style=THEME["primary"])
        table.add_column("Severity", style=THEME["muted"])
        table.add_column("Score", style=THEME["muted"])
        table.add_column("Description", style=THEME["secondary"])

        for cve in results:
            summary = self._extract_summary(cve)
            sev_color = self._severity_style(summary["severity"])
            desc = summary["description"]
            short_desc = desc if len(desc) <= 70 else desc[:67] + "..."
            table.add_row(
                summary["id"],
                f"[bold {sev_color}]{summary['severity']}[/bold {sev_color}]",
                summary["score"],
                short_desc,
            )

        print_centered(console, table)


if __name__ == "__main__":
    mode = console.input(r"  Search by \[i]d or \[k]eyword? ").strip().lower()

    if mode == "i":
        cve_id = console.input("  Enter CVE ID (e.g. CVE-2021-44228): ").strip()
        if cve_id:
            CVELookup().display_by_id(cve_id)
        else:
            console.print("[bold red]No CVE ID entered.[/bold red]")
    elif mode == "k":
        keyword = console.input("  Enter a keyword (e.g. openssl): ").strip()
        if keyword:
            CVELookup().display_by_keyword(keyword)
        else:
            console.print("[bold red]No keyword entered.[/bold red]")
    else:
        console.print("[bold red]Invalid option.[/bold red]")
