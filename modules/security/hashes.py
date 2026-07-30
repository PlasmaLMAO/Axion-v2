import hashlib
from datetime import datetime
from pathlib import Path

from rich.console import Console
from rich.table import Table

console = Console()

CHUNK_SIZE = 65536  # 64 KB per read, balances memory use and speed


class HashAnalyzer:
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
            console.print(f"\n[bold red]File not found:[/bold red] {filepath}\n")
            return None
        if not filepath.is_file():
            console.print(f"\n[bold red]Not a regular file:[/bold red] {filepath}\n")
            return None

        metadata = self.get_metadata(filepath)
        hashes = self.compute_hashes(filepath)
        return {**metadata, **hashes}

    def display(self, filepath_str: str) -> None:
        results = self.analyze(filepath_str)
        if results is None:
            return

        table = Table(title="File Hash Analysis", title_style="bold #e6e6e6")
        table.add_column("Field", style="#999999")
        table.add_column("Value", style="#e6e6e6")

        for key, value in results.items():
            table.add_row(key, value)

        console.print(table)


if __name__ == "__main__":
    filepath_str = console.input("  Enter a file path to analyze: ").strip()
    if filepath_str:
        HashAnalyzer().display(filepath_str)
    else:
        console.print("[bold red]No file path entered.[/bold red]")
