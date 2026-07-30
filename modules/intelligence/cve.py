import requests
from rich.console import Console
from rich.table import Table

console = Console()

NVD_API_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0"
REQUEST_TIMEOUT = 10
RESULTS_LIMIT = 10


class CVELookup:

    def lookup_by_id(self, cve_id: str) -> dict | None:
        try:
            response = requests.get(
                NVD_API_URL,
                params={"cveId": cve_id.upper()},
                timeout=REQUEST_TIMEOUT,
            )
            response.raise_for_status()
        except requests.RequestException as e:
            console.print(f"\n[bold red]Request failed:[/bold red] {e}\n")
            return None

        data = response.json()
        vulnerabilities = data.get("vulnerabilities", [])
        if not vulnerabilities:
            console.print(f"\n[bold red]No results found for:[/bold red] {cve_id}\n")
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
            console.print(f"\n[bold red]Request failed:[/bold red] {e}\n")
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

        # CVSS severity can appear under different metric versions;
        # check newest-to-oldest and use the first one present.
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

    def display_by_id(self, cve_id: str) -> None:
        cve = self.lookup_by_id(cve_id)
        if cve is None:
            return

        summary = self._extract_summary(cve)

        table = Table(title=f"CVE Details: {summary['id']}", title_style="bold #e6e6e6")
        table.add_column("Field", style="#999999")
        table.add_column("Value", style="#e6e6e6")
        table.add_row("Severity", summary["severity"])
        table.add_row("CVSS Score", summary["score"])
        table.add_row("Published", cve.get("published", "-"))
        console.print(table)

        console.print(f"\n[bold #e6e6e6]Description:[/bold #e6e6e6]\n{summary['description']}\n")

    def display_by_keyword(self, keyword: str) -> None:
        results = self.search_by_keyword(keyword)
        if not results:
            console.print(f"\n[dim]No CVEs found matching '{keyword}'.[/dim]\n")
            return

        table = Table(
            title=f"CVE Search Results for '{keyword}' (showing up to {RESULTS_LIMIT})",
            title_style="bold #e6e6e6",
        )
        table.add_column("CVE ID", style="#e6e6e6")
        table.add_column("Severity", style="#999999")
        table.add_column("Score", style="#999999")
        table.add_column("Description", style="#bfbfbf")

        for cve in results:
            summary = self._extract_summary(cve)
            desc = summary["description"]
            short_desc = desc if len(desc) <= 70 else desc[:67] + "..."
            table.add_row(summary["id"], summary["severity"], summary["score"], short_desc)

        console.print(table)


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
