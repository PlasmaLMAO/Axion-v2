import re
from collections import Counter
from pathlib import Path

from rich.console import Console
from rich.table import Table

console = Console()

# Keywords that commonly indicate a security-relevant log line.
# Case-insensitive match.
SUSPICIOUS_KEYWORDS = [
    "failed password", "authentication failure", "unauthorized",
    "denied", "invalid user", "permission denied", "attack",
    "exploit", "malware", "intrusion", "brute force", "root login",
    "segfault", "traceback", "critical", "error",
]

# Pattern to extract an IPv4 address from a log line, used for
# frequency analysis of repeated-source events.
IPV4_PATTERN = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")

FAILED_LOGIN_THRESHOLD = 3  # flag an IP with 3+ failed-login lines


class LogAnalyzer:

    def _read_lines(self, filepath: Path) -> list[str]:
        with filepath.open("r", encoding="utf-8", errors="replace") as f:
            return f.readlines()

    def find_keyword_matches(self, lines: list[str]) -> list[tuple[int, str, str]]:
        matches = []
        for i, line in enumerate(lines, start=1):
            lower_line = line.lower()
            for keyword in SUSPICIOUS_KEYWORDS:
                if keyword in lower_line:
                    matches.append((i, keyword, line.strip()))
                    break  # one match per line is enough to flag it
        return matches

    def find_repeated_failures(self, lines: list[str]) -> dict[str, int]:
        failure_terms = ["failed password", "authentication failure", "invalid user"]
        ip_counts = Counter()

        for line in lines:
            lower_line = line.lower()
            if any(term in lower_line for term in failure_terms):
                ip_match = IPV4_PATTERN.search(line)
                if ip_match:
                    ip_counts[ip_match.group()] += 1

        return {ip: count for ip, count in ip_counts.items() if count >= FAILED_LOGIN_THRESHOLD}

    def analyze(self, filepath_str: str) -> dict | None:
        filepath = Path(filepath_str).expanduser()

        if not filepath.exists():
            console.print(f"\n[bold red]File not found:[/bold red] {filepath}\n")
            return None
        if not filepath.is_file():
            console.print(f"\n[bold red]Not a regular file:[/bold red] {filepath}\n")
            return None

        lines = self._read_lines(filepath)

        return {
            "total_lines": len(lines),
            "keyword_matches": self.find_keyword_matches(lines),
            "repeated_failures": self.find_repeated_failures(lines),
        }

    def display(self, filepath_str: str) -> None:
        results = self.analyze(filepath_str)
        if results is None:
            return

        console.print(f"\n  Total lines scanned: [#e6e6e6]{results['total_lines']}[/#e6e6e6]\n")

        # Repeated failed-login sources
        if results["repeated_failures"]:
            table = Table(title="Repeated Failed Logins (possible brute force)", title_style="bold #e6e6e6")
            table.add_column("Source IP", style="#e6e6e6")
            table.add_column("Failed Attempts", style="#999999", justify="right")
            for ip, count in sorted(results["repeated_failures"].items(), key=lambda x: -x[1]):
                table.add_row(ip, str(count))
            console.print(table)
            console.print()
        else:
            console.print("[dim]No repeated failed-login patterns detected.[/dim]\n")

        # Keyword matches (capped for readability)
        matches = results["keyword_matches"]
        if matches:
            table = Table(title=f"Suspicious Keyword Matches ({len(matches)} total)", title_style="bold #e6e6e6")
            table.add_column("Line", style="#999999", justify="right")
            table.add_column("Keyword", style="#bfbfbf")
            table.add_column("Content", style="#e6e6e6")
            for line_num, keyword, content in matches[:25]:
                display_content = content if len(content) <= 80 else content[:77] + "..."
                table.add_row(str(line_num), keyword, display_content)
            console.print(table)
            if len(matches) > 25:
                console.print(f"\n[dim]... and {len(matches) - 25} more matches not shown.[/dim]")
        else:
            console.print("[dim]No suspicious keywords detected.[/dim]")


if __name__ == "__main__":
    filepath_str = console.input("  Enter a log file path to analyze: ").strip()
    if filepath_str:
        LogAnalyzer().display(filepath_str)
    else:
        console.print("[bold red]No file path entered.[/bold red]")
