import sys
from pathlib import Path as _Path

_PROJECT_ROOT = _Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import re
from collections import Counter
from pathlib import Path

from rich.console import Console, Group

from core.theme import THEME, boxless_table, print_centered

console = Console()

SUSPICIOUS_KEYWORDS = [
    "failed password", "authentication failure", "unauthorized",
    "denied", "invalid user", "permission denied", "attack",
    "exploit", "malware", "intrusion", "brute force", "root login",
    "segfault", "traceback", "critical", "error",
]

IPV4_PATTERN = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")

FAILED_LOGIN_THRESHOLD = 3


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
                    break
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
            print_centered(console, f"[bold {THEME['error']}]File not found:[/bold {THEME['error']}] {filepath}")
            return None
        if not filepath.is_file():
            print_centered(console, f"[bold {THEME['error']}]Not a regular file:[/bold {THEME['error']}] {filepath}")
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

        renderables = [f"Total lines scanned: [{THEME['primary']}]{results['total_lines']}[/{THEME['primary']}]", ""]

        if results["repeated_failures"]:
            table = boxless_table("Repeated Failed Logins (possible brute force)")
            table.add_column("Source IP", style=THEME["primary"])
            table.add_column("Failed Attempts", style=THEME["warning"], justify="right")
            for ip, count in sorted(results["repeated_failures"].items(), key=lambda x: -x[1]):
                table.add_row(ip, str(count))
            renderables.append(table)
        else:
            renderables.append(f"[{THEME['faint']}]No repeated failed-login patterns detected.[/{THEME['faint']}]")

        renderables.append("")

        matches = results["keyword_matches"]
        if matches:
            table = boxless_table(f"Suspicious Keyword Matches ({len(matches)} total)")
            table.add_column("Line", style=THEME["muted"], justify="right")
            table.add_column("Keyword", style=THEME["secondary"])
            table.add_column("Content", style=THEME["primary"])
            for line_num, keyword, content in matches[:25]:
                display_content = content if len(content) <= 80 else content[:77] + "..."
                table.add_row(str(line_num), keyword, display_content)
            renderables.append(table)
            if len(matches) > 25:
                renderables.append(f"[{THEME['faint']}]... and {len(matches) - 25} more matches not shown.[/{THEME['faint']}]")
        else:
            renderables.append(f"[{THEME['faint']}]No suspicious keywords detected.[/{THEME['faint']}]")

        print_centered(console, Group(*renderables))


if __name__ == "__main__":
    filepath_str = console.input("  Enter a log file path to analyze: ").strip()
    if filepath_str:
        LogAnalyzer().display(filepath_str)
    else:
        console.print("[bold red]No file path entered.[/bold red]")
