import sys
from pathlib import Path as _Path

_PROJECT_ROOT = _Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import hashlib
from datetime import datetime
from pathlib import Path

from rich.console import Console

from core.theme import THEME, boxless_table, print_centered

console = Console()

CHUNK_SIZE = 65536


class HashAnalyzer:
    """Computes hashes and metadata for a given file."""

    def compute_hashes(self, filepath: Path) -> dict[str, str]:
        md5 = hashlib.md5()
        sha1 = hashlib.sha1()
        sha256 = hashlib.sha256()

        with filepath.open("rb") as f:
            while chunk := f.read(CHUNK_SIZE):
                md5.update(chunk)
                sha1.update(chunk)
                sha256.update(chunk)

        return {
            "MD5": md5.hexdigest(),
            "SHA1": sha1.hexdigest(),
            "SHA256": sha256.hexdigest(),
        }

    def get_metadata(self, filepath: Path) -> dict[str, str]:
        stat = filepath.stat()
        modified = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
        return {
            "Path": str(filepath.resolve()),
            "Size": f"{stat.st_size:,} bytes",
            "Modified": modified,
        }

    def analyze(self, filepath_str: str) -> dict[str, str] | None:
        filepath = Path(filepath_str).expanduser()

        if not filepath.exists():
            print_centered(console, f"[bold {THEME['error']}]File not found:[/bold {THEME['error']}] {filepath}")
            return None
        if not filepath.is_file():
            print_centered(console, f"[bold {THEME['error']}]Not a regular file:[/bold {THEME['error']}] {filepath}")
            return None

        metadata = self.get_metadata(filepath)
        hashes = self.compute_hashes(filepath)
        return {**metadata, **hashes}

    def display(self, filepath_str: str) -> None:
        results = self.analyze(filepath_str)
        if results is None:
            return

        table = boxless_table("File Hash Analysis")
        table.add_column("Field", style=THEME["muted"])
        table.add_column("Value", style=THEME["primary"])

        for key, value in results.items():
            table.add_row(key, value)

        print_centered(console, table)


if __name__ == "__main__":
    filepath_str = console.input("  Enter a file path to analyze: ").strip()
    if filepath_str:
        HashAnalyzer().display(filepath_str)
    else:
        console.print("[bold red]No file path entered.[/bold red]")
