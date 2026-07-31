
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import requests

from core.config import Config

REQUEST_TIMEOUT = 5

# Discord embed side-bar colors are decimal integers, not hex strings.
# These correspond to our theme's muted semantic colors.
SEVERITY_COLORS = {
    "info": 0x7A9EC9,
    "warning": 0xC9A86A,
    "error": 0xC97A7A,
    "success": 0x7FBF8F,
}


class WebhookNotifier:

    def __init__(self) -> None:
        self.config = Config()

    def is_configured(self) -> bool:
        return bool(self.config.get("webhook_url"))

    def set_url(self, url: str) -> None:
        self.config.set("webhook_url", url)

    def send(self, title: str, description: str, severity: str = "info", fields: dict | None = None) -> bool:
        url = self.config.get("webhook_url")
        if not url:
            return False

        embed = {
            "title": title,
            "description": description,
            "color": SEVERITY_COLORS.get(severity, SEVERITY_COLORS["info"]),
            "footer": {"text": "AXION V2"},
        }

        if fields:
            embed["fields"] = [
                {"name": str(k), "value": str(v), "inline": True}
                for k, v in fields.items()
            ]

        payload = {"embeds": [embed]}

        try:
            response = requests.post(url, json=payload, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            return True
        except requests.RequestException:
            return False


if __name__ == "__main__":
    from rich.console import Console
    console = Console()

    notifier = WebhookNotifier()
    if not notifier.is_configured():
        console.print("[bold red]No webhook configured.[/bold red] Set one with:")
        console.print('  python -c "from core.webhook import WebhookNotifier; WebhookNotifier().set_url(\'YOUR_URL\')"')
    else:
        success = notifier.send(
            title="AXION V2 Test Alert",
            description="This is a test notification from AXION V2.",
            severity="info",
            fields={"Source": "core/webhook.py", "Status": "Test"},
        )
        console.print("[bold green]Sent![/bold green]" if success else "[bold red]Failed to send.[/bold red]")
