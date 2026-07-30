from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()

LOGO_PATH = Path(__file__).resolve().parent.parent / "assets" / "logo.txt"

THEME = {
    "logo": "bold #e6e6e6",
    "border": "#e6e6e6",
    "tagline": "#999999",
    "version": "#777777",
    "menu_key": "bold #e6e6e6",
    "menu_label": "#bfbfbf",
}


class Banner:
    APP_NAME = "AXION V2"
    TAGLINE = "Cybersecurity Suite"
    VERSION = "2.0.0"

    MENU_ITEMS = [
        ("1", "System Information"),
        ("2", "Network Tools"),
        ("3", "Security Tools"),
        ("4", "Intelligence"),
        ("5", "Reports"),
        ("0", "Exit"),
    ]

    def __init__(self, theme: dict = THEME) -> None:
        self.theme = theme

    def _load_logo(self) -> str:
        try:
            return LOGO_PATH.read_text(encoding="utf-8").rstrip("\n")
        except FileNotFoundError:
            return self.APP_NAME

    def show_banner(self) -> None:
        logo_text = Text(self._load_logo(), style=self.theme["logo"], justify="center")
        tagline_text = Text(self.TAGLINE, style=self.theme["tagline"], justify="center")
        version_text = Text(f"v{self.VERSION}", style=self.theme["version"], justify="center")

        console.print(
            Panel.fit(
                Text.assemble(logo_text, "\n\n", tagline_text, "\n", version_text),
                border_style=self.theme["border"],
                padding=(1, 4),
            )
        )
        console.print()

    def show_menu(self) -> None:
        for key, label in self.MENU_ITEMS:
            console.print(
                f"  [{self.theme['menu_key']}][{key}][/{self.theme['menu_key']}] "
                f"[{self.theme['menu_label']}]{label}[/{self.theme['menu_label']}]"
            )
        console.print()

    def render(self) -> None:
        console.clear()
        self.show_banner()
        self.show_menu()


if __name__ == "__main__":
    Banner().render()
