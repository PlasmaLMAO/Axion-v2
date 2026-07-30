import importlib
import pkgutil
import sys
from pathlib import Path
from types import ModuleType

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODULES_DIR = PROJECT_ROOT / "modules"

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

class ModuleLoader:
    def __init__(self, package_name: str = "modules") -> None:
        self.package_name = package_name

    def discover(self) -> list[str]:
        package = importlib.import_module(self.package_name)
        found = []

        for finder, name, is_pkg in pkgutil.walk_packages(
            package.__path__, prefix=f"{self.package_name}."
        ):
            if not is_pkg:
                found.append(name)

        return found

    def load(self, dotted_path: str) -> ModuleType:
        return importlib.import_module(dotted_path)

    def load_all(self) -> dict[str, ModuleType]:
        loaded = {}
        for dotted_path in self.discover():
            try:
                loaded[dotted_path] = self.load(dotted_path)
            except ImportError as e:
                print(f"[module_loader] Failed to load {dotted_path}: {e}")
        return loaded


if __name__ == "__main__":
    loader = ModuleLoader()

    print("Discovered modules:")
    for path in loader.discover():
        print(f"  - {path}")

    print("\nLoading all modules...")
    modules = loader.load_all()
    print(f"\nSuccessfully loaded {len(modules)} module(s).")
