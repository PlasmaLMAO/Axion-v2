import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from rich.console import Console

from core.banner import Banner
from core.config import Config
from core.logger import AxionLogger
from core.database import Database

console = Console()


class AxionApp:

    def __init__(self) -> None:
        self.banner = Banner()
        self.config = Config()
        self.logger = AxionLogger.get_logger()

    def run(self) -> None:
        self.logger.info("AXION V2 session started.")

        with Database():
            pass

        try:
            self._menu_loop()
        except KeyboardInterrupt:
            console.print("\n[dim]Interrupted.[/dim]")
        finally:
            self.logger.info("AXION V2 session ended.")

    def _menu_loop(self) -> None:
        while True:
            self.banner.render()
            choice = console.input("  [bold]Select an option:[/bold] ").strip()

            if choice == "0":
                console.print("\nExiting AXION V2. Goodbye.\n")
                break
            elif choice in {"1", "2", "3", "4", "5"}:
                self._handle_placeholder(choice)
            else:
                console.print("\n[bold red]Invalid option.[/bold red] Press Enter to try again.")
                console.input()

    def _handle_placeholder(self, choice: str) -> None:
        labels = {
            "1": "System Information",
            "2": "Network Tools",
            "3": "Security Tools",
            "4": "Intelligence",
            "5": "Reports",
        }
        console.print(f"\n[dim]{labels[choice]} — not yet implemented (coming in a later phase).[/dim]")
        self.logger.debug(f"User selected menu option {choice} ({labels[choice]}) — placeholder.")
        console.input("\nPress Enter to return to the menu.")


if __name__ == "__main__":
    AxionApp().run()
