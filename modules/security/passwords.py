import math
import re

from rich.console import Console
from rich.table import Table

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
            pool_size += 32  # approximate size of common symbol set

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

    def display(self, password: str) -> None:
        """Analyze a password and print results. Never logs the password itself."""
        entropy = self.calculate_entropy(password)
        is_common = self.check_common_password(password)
        warnings = self.check_patterns(password)
        rating = self.rate_strength(entropy, is_common, len(warnings))

        table = Table(title="Password Strength Analysis", title_style="bold #e6e6e6")
        table.add_column("Field", style="#999999")
        table.add_column("Value", style="#e6e6e6")

        table.add_row("Length", str(len(password)))
        table.add_row("Estimated Entropy", f"{entropy:.1f} bits")
        table.add_row("Common Password", "Yes" if is_common else "No")
        table.add_row("Rating", rating)

        console.print(table)

        if warnings:
            console.print("\n[bold #e6e6e6]Warnings:[/bold #e6e6e6]")
            for warning in warnings:
                console.print(f"  - [#999999]{warning}[/#999999]")
        else:
            console.print("\n[dim]No pattern-based warnings.[/dim]")


if __name__ == "__main__":
    import getpass

    password = getpass.getpass("  Enter a password to audit (input hidden): ")
    if password:
        PasswordAuditor().display(password)
    else:
        console.print("[bold red]No password entered.[/bold red]")
