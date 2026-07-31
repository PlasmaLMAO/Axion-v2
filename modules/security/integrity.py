import sys
from pathlib import Path as _Path

_PROJECT_ROOT = _Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import hashlib
from datetime import datetime
from pathlib import Path

from rich.console import Console

from core.database import Database
from core.theme import THEME, boxless_table, print_centered

console = Console()

CHUNK_SIZE = 65536

TABLE_SCHEMA = """
    CREATE TABLE IF NOT EXISTS integrity_baseline (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        baseline_name TEXT NOT NULL,
        filepath TEXT NOT NULL,
        sha256 TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(baseline_name, filepath)
    )
"""


class IntegrityMonitor:

    def __init__(self) -> None:
        with Database() as db:
            db.execute(TABLE_SCHEMA)

    def _hash_file(self, filepath: Path) -> str:
        sha256 = hashlib.sha256()
        with filepath.open("rb") as f:
            while chunk := f.read(CHUNK_SIZE):
                sha256.update(chunk)
        return sha256.hexdigest()

    def _collect_files(self, directory: Path) -> list[Path]:
        return [p for p in directory.rglob("*") if p.is_file()]

    def create_baseline(self, directory_str: str, baseline_name: str) -> int:
        directory = Path(directory_str).expanduser().resolve()
        if not directory.is_dir():
            print_centered(console, f"[bold {THEME['error']}]Not a directory:[/bold {THEME['error']}] {directory}")
            return 0

        files = self._collect_files(directory)

        with Database() as db:
            db.execute(
                "DELETE FROM integrity_baseline WHERE baseline_name = ?",
                (baseline_name,),
            )
            for filepath in files:
                file_hash = self._hash_file(filepath)
                db.execute(
                    """INSERT INTO integrity_baseline
                       (baseline_name, filepath, sha256) VALUES (?, ?, ?)""",
                    (baseline_name, str(filepath), file_hash),
                )

        print_centered(
            console,
            f"[bold {THEME['primary']}]Baseline '{baseline_name}' created:[/bold {THEME['primary']}] "
            f"{len(files)} file(s) recorded.",
        )
        return len(files)

    def compare_baseline(self, baseline_name: str) -> tuple[list[str], list[str]] | None:
        with Database() as db:
            rows = db.fetch_all(
                "SELECT filepath, sha256 FROM integrity_baseline WHERE baseline_name = ?",
                (baseline_name,),
            )

        if not rows:
            print_centered(console, f"[bold {THEME['error']}]No baseline found named '{baseline_name}'.[/bold {THEME['error']}]")
            return None

        modified = []
        deleted = []
        unchanged_count = 0

        for row in rows:
            filepath = Path(row["filepath"])
            if not filepath.exists():
                deleted.append(str(filepath))
                continue

            current_hash = self._hash_file(filepath)
            if current_hash != row["sha256"]:
                modified.append(str(filepath))
            else:
                unchanged_count += 1

        table = boxless_table(f"Integrity Check: {baseline_name}")
        table.add_column("Status", style=THEME["muted"])
        table.add_column("File", style=THEME["primary"])

        for filepath in modified:
            table.add_row(f"[bold {THEME['warning']}]MODIFIED[/bold {THEME['warning']}]", filepath)
        for filepath in deleted:
            table.add_row(f"[bold {THEME['error']}]DELETED[/bold {THEME['error']}]", filepath)

        if modified or deleted:
            print_centered(console, table)
        else:
            print_centered(console, f"[{THEME['faint']}]No changes detected.[/{THEME['faint']}]")

        print_centered(
            console,
            f"Unchanged: {unchanged_count}  |  Modified: {len(modified)}  |  Deleted: {len(deleted)}",
        )

        return modified, deleted


if __name__ == "__main__":
    action = console.input("  \\[c]reate baseline or \\[v]erify against one? ").strip().lower()

    if action == "c":
        directory = console.input("  Directory to baseline: ").strip()
        name = console.input("  Baseline name: ").strip()
        if directory and name:
            IntegrityMonitor().create_baseline(directory, name)
        else:
            console.print("[bold red]Directory and name are required.[/bold red]")
    elif action == "v":
        name = console.input("  Baseline name to verify: ").strip()
        if name:
            IntegrityMonitor().compare_baseline(name)
        else:
            console.print("[bold red]Baseline name is required.[/bold red]")
    else:
        console.print("[bold red]Invalid option.[/bold red]")
