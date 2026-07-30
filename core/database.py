import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "data" / "database.db"


class Database:
    def __init__(self, path: Path = DB_PATH) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(self.path)
        self._conn.row_factory = sqlite3.Row  # access columns by name
        self._conn.execute("PRAGMA foreign_keys = ON")

    def execute(self, query: str, params: tuple = ()) -> sqlite3.Cursor:
        cursor = self._conn.execute(query, params)
        self._conn.commit()
        return cursor

    def fetch_all(self, query: str, params: tuple = ()) -> list[sqlite3.Row]:
        cursor = self._conn.execute(query, params)
        return cursor.fetchall()

    def fetch_one(self, query: str, params: tuple = ()) -> sqlite3.Row | None:
        cursor = self._conn.execute(query, params)
        return cursor.fetchone()

    def close(self) -> None:
        self._conn.close()

    def __enter__(self) -> "Database":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()


if __name__ == "__main__":
    with Database() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS test_table (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        db.execute(
            "INSERT INTO test_table (message) VALUES (?)",
            ("Database connection successful",),
        )
        rows = db.fetch_all("SELECT * FROM test_table")
        for row in rows:
            print(f"[{row['id']}] {row['message']} @ {row['created_at']}")
