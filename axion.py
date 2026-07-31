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
from core.report_generator import ReportGenerator
from core.cli import CLI
from core.webhook import WebhookNotifier
from core.theme import THEME

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
from modules.system.dashboard import Dashboard

console = Console()


class AxionApp:

    def __init__(self) -> None:
        self.banner = Banner()
        self.config = Config()
        self.logger = AxionLogger.get_logger()
        self.reports = ReportGenerator()
        self.webhook = WebhookNotifier()
        self.cli = CLI(prompt="axion> ")
        self._register_commands()

    def _offer_report(self, title: str, data) -> None:
        if not data:
            return
        save = console.input(f"\n[{THEME['secondary']}]Save this as a report? [y/N]:[/{THEME['secondary']}] ").strip().lower()
        if save == "y":
            json_path, html_path = self.reports.save_both(title, data)
            console.print(f"[{THEME['faint']}]Saved:[/{THEME['faint']}] {json_path.name}")
            console.print(f"[{THEME['faint']}]Saved:[/{THEME['faint']}] {html_path.name}")
            self.logger.info(f"Report saved: {title}")


    def _cmd_sysinfo(self) -> None:
        self.logger.debug("Ran System Information.")
        info = SystemInfo()
        info.display()
        report_data = {
            **info.get_os_info(),
            "Uptime": info.get_uptime(),
            **{f"CPU {k}": v for k, v in info.get_cpu_info().items()},
            **{f"Memory {k}": v for k, v in info.get_memory_info().items()},
            **{f"Disk {k}": v for k, v in info.get_disk_info().items()},
        }
        self._offer_report("System Information", report_data)

    def _cmd_processes(self) -> None:
        self.logger.debug("Ran Process Viewer.")
        ProcessViewer().display()

    def _cmd_dashboard(self) -> None:
        self.logger.debug("Launched live dashboard.")
        Dashboard().run()

    def _cmd_netinfo(self) -> None:
        self.logger.debug("Ran Network Scanner.")
        scanner = NetworkScanner()
        scanner.display()
        report_data = {
            "Hostname": scanner.get_hostname(),
            "Primary IP": scanner.get_local_ip(),
            "Interfaces": scanner.get_interfaces(),
        }
        self._offer_report("Network Interfaces", report_data)

    def _cmd_dns(self, domain: str) -> None:
        self.logger.debug(f"Ran DNS Analyzer on {domain}.")
        dns_tool = DNSAnalyzer()
        dns_tool.display(domain)
        report_data = dns_tool.analyze(domain)
        self._offer_report(f"DNS Analysis - {domain}", report_data)

    def _cmd_connections(self) -> None:
        self.logger.debug("Ran Connection Monitor.")
        monitor = ConnectionMonitor()
        monitor.display()
        report_data = monitor.get_connections()
        self._offer_report("Active Connections", report_data)

    def _cmd_portscan(self, target: str) -> None:
        self.logger.debug(f"Ran Port Scanner on {target}.")
        PortScanner().display(target)


    def _cmd_hash(self, filepath: str) -> None:
        self.logger.debug("Ran Hash Analyzer.")
        analyzer = HashAnalyzer()
        result = analyzer.analyze(filepath)
        if result:
            analyzer.display(filepath)
            self._offer_report(f"Hash Analysis - {filepath}", result)

    def _cmd_password(self) -> None:
        password = getpass.getpass("Enter a password to audit (input hidden): ")
        if password:
            self.logger.debug("Ran Password Auditor.")
            PasswordAuditor().display(password)

    def _cmd_baseline(self, directory: str, name: str) -> None:
        self.logger.debug(f"Created integrity baseline '{name}'.")
        IntegrityMonitor().create_baseline(directory, name)

    def _cmd_verify(self, name: str) -> None:
        self.logger.debug(f"Verified integrity baseline '{name}'.")
        monitor = IntegrityMonitor()
        changes = monitor.compare_baseline(name)
        if changes and self.webhook.is_configured():
            modified, deleted = changes
            if modified or deleted:
                self.webhook.send(
                    title="File Integrity Change Detected",
                    description=f"Baseline '{name}' verification found changes.",
                    severity="error",
                    fields={"Modified": len(modified), "Deleted": len(deleted)},
                )

    def _cmd_logscan(self, filepath: str) -> None:
        self.logger.debug("Ran Log Analyzer.")
        analyzer = LogAnalyzer()
        result = analyzer.analyze(filepath)
        if result:
            analyzer.display(filepath)
            report_data = {
                "total_lines": result["total_lines"],
                "repeated_failures": result["repeated_failures"],
                "keyword_match_count": len(result["keyword_matches"]),
            }
            if result["repeated_failures"] and self.webhook.is_configured():
                top_ip = max(result["repeated_failures"], key=result["repeated_failures"].get)
                self.webhook.send(
                    title="Brute Force Pattern Detected",
                    description=f"Log analysis of `{filepath}` found repeated failed logins.",
                    severity="warning",
                    fields={
                        "Top Source IP": top_ip,
                        "Attempts": result["repeated_failures"][top_ip],
                        "Flagged IPs": len(result["repeated_failures"]),
                    },
                )
            self._offer_report(f"Log Analysis - {filepath}", report_data)


    def _cmd_ip(self, ip: str = "") -> None:
        self.logger.debug(f"Ran IP Lookup on '{ip or 'self'}'.")
        ip_tool = IPLookup()
        data = ip_tool.lookup(ip)
        if data:
            ip_tool.display(ip)
            self._offer_report(f"IP Lookup - {ip or 'self'}", data)

    def _cmd_cve_id(self, cve_id: str) -> None:
        self.logger.debug(f"Looked up CVE {cve_id}.")
        lookup = CVELookup()
        cve = lookup.lookup_by_id(cve_id)
        if cve:
            lookup.display_by_id(cve_id)
            summary = lookup._extract_summary(cve)
            self._offer_report(f"CVE Lookup - {cve_id}", summary)

    def _cmd_cve_search(self, keyword: str) -> None:
        self.logger.debug(f"Searched CVEs for keyword '{keyword}'.")
        lookup = CVELookup()
        results = lookup.search_by_keyword(keyword)
        if results:
            lookup.display_by_keyword(keyword)
            summaries = [lookup._extract_summary(c) for c in results]
            self._offer_report(f"CVE Search - {keyword}", summaries)


    def _cmd_config_webhook(self, url: str) -> None:
        self.webhook.set_url(url)
        console.print(f"[{THEME['success']}]Webhook URL saved.[/{THEME['success']}]")

    def _cmd_config_test(self) -> None:
        if not self.webhook.is_configured():
            console.print(f"[{THEME['error']}]No webhook configured. Use: config-webhook <url>[/{THEME['error']}]")
            return
        success = self.webhook.send(
            title="AXION V2 Test Alert",
            description="This is a test notification from AXION V2.",
            severity="info",
        )
        if success:
            console.print(f"[{THEME['success']}]Test alert sent.[/{THEME['success']}]")
        else:
            console.print(f"[{THEME['error']}]Failed to send test alert.[/{THEME['error']}]")


    def _register_commands(self) -> None:
        r = self.cli.register

        r("sysinfo", self._cmd_sysinfo, "Show OS, CPU, RAM, disk, and GPU info.", "System")
        r("processes", self._cmd_processes, "List running processes by resource usage.", "System")
        r("dashboard", self._cmd_dashboard, "Launch a live-updating system dashboard (Ctrl+C to exit).", "System")

        r("netinfo", self._cmd_netinfo, "Show local network interfaces and IP.", "Network")
        r("dns", self._cmd_dns, "Look up DNS records. Usage: dns <domain>", "Network")
        r("connections", self._cmd_connections, "List active network connections.", "Network")
        r("portscan", self._cmd_portscan, "Scan common ports. Usage: portscan <target> (localhost/private only)", "Network")

        r("hash", self._cmd_hash, "Compute file hashes. Usage: hash <filepath>", "Security")
        r("password", self._cmd_password, "Audit password strength (hidden input).", "Security")
        r("baseline", self._cmd_baseline, "Create integrity baseline. Usage: baseline <dir> <name>", "Security")
        r("verify", self._cmd_verify, "Verify against a baseline. Usage: verify <name>", "Security")
        r("logscan", self._cmd_logscan, "Scan a log file for suspicious patterns. Usage: logscan <filepath>", "Security")

        r("ip", self._cmd_ip, "Look up IP geolocation/ASN. Usage: ip [address] (blank = your own)", "Intelligence")
        r("cve", self._cmd_cve_id, "Look up a CVE by ID. Usage: cve <CVE-YYYY-NNNNN>", "Intelligence")
        r("cve-search", self._cmd_cve_search, "Search CVEs by keyword. Usage: cve-search <keyword>", "Intelligence")

        r("config-webhook", self._cmd_config_webhook, "Set your Discord webhook URL. Usage: config-webhook <url>", "Config")
        r("config-test", self._cmd_config_test, "Send a test alert to your configured webhook.", "Config")

    def run_one_shot(self, argv: list[str]) -> None:
            self.logger.info(f"AXION V2 one-shot command: {' '.join(argv)}")
            with Database():
                pass

            line = " ".join(argv)
            self.cli.dispatch(line)

            self.logger.info("AXION V2 one-shot session ended.")
    
    def run(self) -> None:
        """Start the interactive REPL."""
        self.logger.info("AXION V2 session started.")
        with Database():
            pass

        self.banner.render()
        console.print(f"[{THEME['faint']}]Type 'help' to see all commands, 'exit' to quit.[/{THEME['faint']}]\n")

        try:
            self.cli.run()
        except KeyboardInterrupt:
            console.print(f"\n[{THEME['muted']}]Interrupted.[/{THEME['muted']}]")
        finally:
            console.print(f"\n[{THEME['secondary']}]Exiting AXION V2. Goodbye.[/{THEME['secondary']}]\n")
            self.logger.info("AXION V2 session ended.")

if __name__ == "__main__":
    app = AxionApp()
    if len(sys.argv) > 1:
        # Arguments given: run one command and exit (e.g. `python axion.py hash README.md`)
        app.run_one_shot(sys.argv[1:])
    else:
        # No arguments: launch the interactive REPL
        app.run()
