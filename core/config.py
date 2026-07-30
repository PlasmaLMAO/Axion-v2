import json
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = PROJECT_ROOT / "data" / "config.json"

DEFAULT_CONFIG = {
    "app_name": "AXION V2",
    "version": "2.0.0",
    "theme": "monochrome",
    "database_path": "data/database.db",
    "log_path": "logs/axion.log",
    "reports_path": "data/reports",
}

class Config:
    def __init__(self, path: Path = CONFIG_PATH) -> None:
        self.path = path
        self._data: dict[str, Any] = {}
        self._load()

    def _load(self) -> None:
        if not self.path.exists():
            self._data = DEFAULT_CONFIG.copy()
            self._save()
            return
        try:
            with self.path.open("r", encoding="utf-8") as f:
                self._data = json.load(f)
        except (json.JSONDecodeError, OSerror):
            self._data = DEFAULT_CONFIG.copy()
            self._save()

    def _save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=4)
            f.write("\n")

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self._data[key] = value
        self._save()

    def all(self) -> dict[str, Any]:
        return self._data.copy()

if __name__ == "__main__":
    cfg = Config()
    print("Loaded config:")
    for key, value in cfg.all().items():
        print(f" {key}: {value}")

