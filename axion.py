import getpass
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

from modules.system.info import SystemInfo
from modules.system.processes import ProcessViewer
from modules.network.scanner import NetworkScanner
from modules.network.dns_analyzer import DNSAnalyzer
from modules.network.connections import ConnectionMonitor
from modules.network.port_scanner import PortScanner
from modules.security.hashes import HashAnalyzer
from modules.security.passwords import PasswordAuditor
from modules.security.integrity import IntegrityMonitor
from modules.security.logs import LogAnalyzer
from modules.intelligence.ip_lookup import IPLookup
from modules.intelligence.cve import CVELookup

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
            self._main_menu()
        except KeyboardInterrupt:
            console.print("\n[dim]Interrupted.[/dim]")
        finally:
            self.logger.info("AXION V2 session ended.")

    def _pause(self) -> None:
        console.input("\nPress Enter to continue.")


    def _main_menu(self) -> None:
        while True:
            self.banner.render()
            choice = console.input("  [bold]Select an option:[/bold] ").strip()

            if choice == "0":
                console.print("\nExiting AXION V2. Goodbye.\n")
                break
            elif choice == "1":
                self._system_menu()
            elif choice == "2":
                self._network_menu()
            elif choice == "3":
                self._security_menu()
            elif choice == "4":
                self._intelligence_menu()
            elif choice == "5":
                console.print("\n[dim]Reports — not yet implemented (Phase 6).[/dim]")
                self._pause()
            else:
                console.print("\n[bold red]Invalid option.[/bold red]")
                self._pause()


    def _system_menu(self) -> None:
        while True:
            console.clear()
            console.print("[bold #e6e6e6]System Tools[/bold #e6e6e6]\n")
            console.print(r"  \[1] System Information")
            console.print(r"  \[2] Running Processes")
            console.print(r"  \[0] Back")
            choice = console.input("\n  Select: ").strip()

            if choice == "0":
                return
            elif choice == "1":
                self.logger.debug("Ran System Information.")
                SystemInfo().display()
                self._pause()
            elif choice == "2":
                self.logger.debug("Ran Process Viewer.")
                ProcessViewer().display()
                self._pause()
            else:
                console.print("\n[bold red]Invalid option.[/bold red]")
                self._pause()


    def _network_menu(self) -> None:
        while True:
            console.clear()
            console.print("[bold #e6e6e6]Network Tools[/bold #e6e6e6]\n")
            console.print(r"  \[1] Local Network Info")
            console.print(r"  \[2] DNS Analyzer")
            console.print(r"  \[3] Connection Monitor")
            console.print(r"  \[4] Port Scanner (localhost / private ranges only)")
            console.print(r"  \[0] Back")
            choice = console.input("\n  Select: ").strip()

            if choice == "0":
                return
            elif choice == "1":
                self.logger.debug("Ran Network Scanner.")
                NetworkScanner().display()
                self._pause()
            elif choice == "2":
                domain = console.input("  Enter a domain (e.g. example.com): ").strip()
                if domain:
                    self.logger.debug(f"Ran DNS Analyzer on {domain}.")
                    DNSAnalyzer().display(domain)
                self._pause()
            elif choice == "3":
                self.logger.debug("Ran Connection Monitor.")
                ConnectionMonitor().display()
                self._pause()
            elif choice == "4":
                target = console.input(
                    "  Enter a target (localhost/private IPs only): "
                ).strip()
                if target:
                    self.logger.debug(f"Ran Port Scanner on {target}.")
                    PortScanner().display(target)
                self._pause()
            else:
                console.print("\n[bold red]Invalid option.[/bold red]")
                self._pause()


    def _security_menu(self) -> None:
        while True:
            console.clear()
            console.print("[bold #e6e6e6]Security Tools[/bold #e6e6e6]\n")
            console.print(r"  \[1] Hash Analyzer")
            console.print(r"  \[2] Password Auditor")
            console.print(r"  \[3] File Integrity Monitor")
            console.print(r"  \[4] Log Analyzer")
            console.print(r"  \[0] Back")
            choice = console.input("\n  Select: ").strip()

            if choice == "0":
                return
            elif choice == "1":
                filepath = console.input("  Enter a file path to hash: ").strip()
                if filepath:
                    self.logger.debug("Ran Hash Analyzer.")
                    HashAnalyzer().display(filepath)
                self._pause()
            elif choice == "2":
                password = getpass.getpass("  Enter a password to audit (input hidden): ")
                if password:
                    self.logger.debug("Ran Password Auditor.")
                    PasswordAuditor().display(password)
                self._pause()
            elif choice == "3":
                self._integrity_submenu()
            elif choice == "4":
                filepath = console.input("  Enter a log file path: ").strip()
                if filepath:
                    self.logger.debug("Ran Log Analyzer.")
                    LogAnalyzer().display(filepath)
                self._pause()
            else:
                console.print("\n[bold red]Invalid option.[/bold red]")
                self._pause()

    def _integrity_submenu(self) -> None:
        action = console.input(r"  \[c]reate baseline or \[v]erify against one? ").strip().lower()
        monitor = IntegrityMonitor()
        if action == "c":
            directory = console.input("  Directory to baseline: ").strip()
            name = console.input("  Baseline name: ").strip()
            if directory and name:
                self.logger.debug(f"Created integrity baseline '{name}'.")
                monitor.create_baseline(directory, name)
        elif action == "v":
            name = console.input("  Baseline name to verify: ").strip()
            if name:
                self.logger.debug(f"Verified integrity baseline '{name}'.")
                monitor.compare_baseline(name)
        else:
            console.print("\n[bold red]Invalid option.[/bold red]")
        self._pause()

    def _intelligence_menu(self) -> None:
        while True:
            console.clear()
            console.print("[bold #e6e6e6]Intelligence[/bold #e6e6e6]\n")
            console.print(r"  \[1] IP Lookup")
            console.print(r"  \[2] CVE Lookup")
            console.print(r"  \[0] Back")
            choice = console.input("\n  Select: ").strip()

            if choice == "0":
                return
            elif choice == "1":
                ip = console.input(
                    "  Enter an IP (blank for your own public IP): "
                ).strip()
                self.logger.debug(f"Ran IP Lookup on '{ip or 'self'}'.")
                IPLookup().display(ip)
                self._pause()
            elif choice == "2":
                self._cve_submenu()
            else:
                console.print("\n[bold red]Invalid option.[/bold red]")
                self._pause()

    def _cve_submenu(self) -> None:
        mode = console.input(r"  Search by \[i]d or \[k]eyword? ").strip().lower()
        lookup = CVELookup()
        if mode == "i":
            cve_id = console.input("  Enter CVE ID (e.g. CVE-2021-44228): ").strip()
            if cve_id:
                self.logger.debug(f"Looked up CVE {cve_id}.")
                lookup.display_by_id(cve_id)
        elif mode == "k":
            keyword = console.input("  Enter a keyword (e.g. openssl): ").strip()
            if keyword:
                self.logger.debug(f"Searched CVEs for keyword '{keyword}'.")
                lookup.display_by_keyword(keyword)
        else:
            console.print("\n[bold red]Invalid option.[/bold red]")
        self._pause()


if __name__ == "__main__":
    AxionApp().run()
