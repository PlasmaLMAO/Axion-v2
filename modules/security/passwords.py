import sys
from pathlib import Path as _Path

_PROJECT_ROOT = _Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import math
import re

from rich.console import Console, Group

from core.theme import THEME, boxless_table, print_centered

console = Console()

COMMON_PASSWORDS = {
    "password", "123456", "12345678", "qwerty", "abc123", "password1",
    "111111", "letmein", "admin", "welcome", "monkey", "iloveyou",
    "123456789", "password123", "1234567890", "dragon", "master",
}


class PasswordAuditor:

    def calculate_entropy(self, password: str) -> float:
        pool_size = 0
        if re.search(r"[a-z]", password):
            pool_size += 26
        if re.search(r"[A-Z]", password):
            pool_size += 26
        if re.search(r"[0-9]", password):
            pool_size += 10
        if re.search(r"[^a-zA-Z0-9]", password):
            pool_size += 32

        if pool_size == 0 or len(password) == 0:
            return 0.0

        return len(password) * math.log2(pool_size)

    def check_common_password(self, password: str) -> bool:
        return password.lower() in COMMON_PASSWORDS

    def check_patterns(self, password: str) -> list[str]:
        warnings = []

        if len(password) < 8:
            warnings.append("Shorter than 8 characters.")
        if re.search(r"(.)\1{2,}", password):
            warnings.append("Contains 3+ repeated characters in a row.")
        if re.search(r"(012|123|234|345|456|567|678|789|890)", password):
            warnings.append("Contains a sequential number pattern.")
        if re.search(r"(abc|bcd|cde|def|efg|qwe|wer|asd|zxc)", password.lower()):
            warnings.append("Contains a sequential keyboard/alphabet pattern.")
        if not re.search(r"[A-Z]", password):
            warnings.append("No uppercase letters.")
        if not re.search(r"[a-z]", password):
            warnings.append("No lowercase letters.")
        if not re.search(r"[0-9]", password):
            warnings.append("No digits.")
        if not re.search(r"[^a-zA-Z0-9]", password):
            warnings.append("No symbols.")

        return warnings

    def rate_strength(self, entropy: float, is_common: bool, warning_count: int) -> str:
        if is_common:
            return "Very Weak (common password)"
        if entropy < 28:
            return "Very Weak"
        if entropy < 36:
            return "Weak"
        if entropy < 60:
            return "Moderate" if warning_count <= 2 else "Weak"
        if entropy < 80:
            return "Strong" if warning_count <= 1 else "Moderate"
        return "Very Strong" if warning_count == 0 else "Strong"

    def _rating_color(self, rating: str) -> str:
        if "Very Weak" in rating or rating == "Weak":
            return THEME["error"]
        if rating == "Moderate":
            return THEME["warning"]
        return THEME["success"]

    def display(self, password: str) -> None:
        entropy = self.calculate_entropy(password)
        is_common = self.check_common_password(password)
        warnings = self.check_patterns(password)
        rating = self.rate_strength(entropy, is_common, len(warnings))
        rating_color = self._rating_color(rating)

        table = boxless_table("Password Strength Analysis")
        table.add_column("Field", style=THEME["muted"])
        table.add_column("Value", style=THEME["primary"])

        table.add_row("Length", str(len(password)))
        table.add_row("Estimated Entropy", f"{entropy:.1f} bits")
        table.add_row("Common Password", "Yes" if is_common else "No")
        table.add_row("Rating", f"[bold {rating_color}]{rating}[/bold {rating_color}]")

        renderables = [table, ""]

        if warnings:
            renderables.append(f"[bold {THEME['primary']}]Warnings:[/bold {THEME['primary']}]")
            for warning in warnings:
                renderables.append(f"  - [{THEME['muted']}]{warning}[/{THEME['muted']}]")
        else:
            renderables.append(f"[{THEME['faint']}]No pattern-based warnings.[/{THEME['faint']}]")

        print_centered(console, Group(*renderables))


if __name__ == "__main__":
    import getpass

    password = getpass.getpass("  Enter a password to audit (input hidden): ")
    if password:
        PasswordAuditor().display(password)
    else:
        console.print("[bold red]No password entered.[/bold red]")
