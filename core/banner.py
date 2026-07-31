import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from rich.console import Console
from rich.text import Text
from rich.align import Align

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
        logo_gradient.justify = "center"
        console.print(Align.center(logo_gradient))

        tagline_text = Text(self.TAGLINE, style=self.theme["secondary"])
        version_text = Text(f"v{self.VERSION}", style=self.theme["faint"])
        console.print(Align.center(tagline_text))
        console.print(Align.center(version_text))
        console.print()

    def render(self) -> None:
        console.clear()
        self.show_banner()


if __name__ == "__main__":
    Banner().render()
