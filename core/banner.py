import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from core.theme import THEME, gradient_lines

console = Console()

LOGO_PATH = Path(__file__).resolve().parent.parent / "assets" / "logo.txt"


class Banner:

    APP_NAME = "AXION V2"
    TAGLINE = "Cybersecurity Suite"
    VERSION = "2.0.0"


    def __init__(self, theme: dict = THEME) -> None:
        self.theme = theme

    def _load_logo(self) -> str:
        try:
            return LOGO_PATH.read_text(encoding="utf-8").rstrip("\n")
        except FileNotFoundError:
            return self.APP_NAME

    def show_banner(self) -> None:
        logo_gradient = gradient_lines(self._load_logo())
        tagline_text = Text(self.TAGLINE, style=self.theme["secondary"], justify="center")
        version_text = Text(f"v{self.VERSION}", style=self.theme["faint"], justify="center")

        logo_gradient.justify = "center"

        console.print(
            Panel.fit(
                Text.assemble(logo_gradient, "\n\n", tagline_text, "\n", version_text),
                border_style=self.theme["border"],
                padding=(1, 4),
            )
        )
        console.print()


    def render(self) -> None:
            """Convenience method: clear screen and show the banner."""
            console.clear()
            self.show_banner()

if __name__ == "__main__":
    Banner().render()
