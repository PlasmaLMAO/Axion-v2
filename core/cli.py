
import shlex
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from rich.console import Console

from core.theme import THEME

console = Console()


class Command:

    def __init__(self, name: str, handler, help_text: str, category: str = "General"):
        self.name = name
        self.handler = handler
        self.help_text = help_text
        self.category = category


class CLI:

    def __init__(self, prompt: str = "axion> ") -> None:
        self.prompt = prompt
        self.commands: dict[str, Command] = {}
        self.running = True

    def register(self, name: str, handler, help_text: str, category: str = "General") -> None:
        self.commands[name] = Command(name, handler, help_text, category)

    def _parse(self, line: str) -> tuple[str, list[str]]:
        try:
            tokens = shlex.split(line)
        except ValueError as e:
            # Unmatched quotes, etc. — treat as a parse error, not a crash.
            console.print(f"[{THEME['error']}]Parse error: {e}[/{THEME['error']}]")
            return "", []

        if not tokens:
            return "", []
        return tokens[0].lower(), tokens[1:]

    def dispatch(self, line: str) -> None:
        line = line.strip()
        if not line:
            return

        name, args = self._parse(line)
        if not name:
            return

        if name in ("exit", "quit"):
            self.running = False
            return

        if name in ("help", "-help", "--help"):
            self._show_help(args[0] if args else None)
            return

        command = self.commands.get(name)
        if command is None:
            console.print(
                f"[{THEME['error']}]Unknown command:[/{THEME['error']}] '{name}'. "
                f"Type 'help' to see available commands."
            )
            return

        try:
            command.handler(*args)
        except TypeError as e:
            console.print(
                f"[{THEME['error']}]Invalid arguments for '{name}':[/{THEME['error']}] {e}"
            )
        except Exception as e:
            console.print(f"[{THEME['error']}]Error running '{name}':[/{THEME['error']}] {e}")

    def _show_help(self, topic: str | None = None) -> None:
        if topic:
            command = self.commands.get(topic.lower())
            if command:
                console.print(f"\n[{THEME['primary']}]{command.name}[/{THEME['primary']}]")
                console.print(f"  {command.help_text}\n")
            else:
                console.print(f"[{THEME['error']}]No such command: '{topic}'[/{THEME['error']}]")
            return

        categories: dict[str, list[Command]] = {}
        for command in self.commands.values():
            categories.setdefault(command.category, []).append(command)

        console.print(f"\n[{THEME['primary']}]Available commands:[/{THEME['primary']}]\n")
        for category, cmds in categories.items():
            console.print(f"[{THEME['secondary']}]{category}[/{THEME['secondary']}]")
            for cmd in sorted(cmds, key=lambda c: c.name):
                console.print(f"  [{THEME['primary']}]{cmd.name:<20}[/{THEME['primary']}] {cmd.help_text}")
            console.print()
        console.print(f"[{THEME['faint']}]Type 'help <command>' for details on one command.[/{THEME['faint']}]")
        console.print(f"[{THEME['faint']}]Type 'exit' or 'quit' to leave.[/{THEME['faint']}]\n")

    def run(self) -> None:
        while self.running:
            try:
                line = console.input(f"[{THEME['primary']}]{self.prompt}[/{THEME['primary']}]")
            except (EOFError, KeyboardInterrupt):
                console.print()
                break
            self.dispatch(line)


if __name__ == "__main__":
    # Standalone smoke test with two fake commands
    def hello(name: str = "world"):
        console.print(f"Hello, {name}!")

    def add(a: str, b: str):
        console.print(f"{a} + {b} = {int(a) + int(b)}")

    cli = CLI()
    cli.register("hello", hello, "Say hello. Usage: hello [name]", category="Demo")
    cli.register("add", add, "Add two numbers. Usage: add <a> <b>", category="Demo")
    cli.run()
