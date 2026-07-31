# AXION V2

A modular, terminal-first cybersecurity toolkit built in Python. Command-driven, defensive-security-focused, and built for learning real Python architecture, networking, and security concepts from the ground up.

```
     █████╗ ██╗  ██╗██╗ ██████╗ ███╗   ██╗
    ██╔══██╗╚██╗██╔╝██║██╔═══██╗████╗  ██║
    ███████║ ╚███╔╝ ██║██║   ██║██╔██╗ ██║
    ██╔══██║ ██╔██╗ ██║██║   ██║██║╚██╗██║
    ██║  ██║██╔╝ ██╗██║╚██████╔╝██║ ╚████║
    ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝ ╚═════╝ ╚═╝  ╚═══╝

axion> hash README.md
```

## What is this?

AXION V2 is a cybersecurity suite covering system auditing, network analysis, security scanning, and threat intelligence lookups — all from one command-driven terminal interface. It's built entirely for **defensive security, auditing, and education**. There is no offensive/exploitation tooling in this project by design.

Every tool works two ways:

```bash
# Interactive REPL — launches a persistent command prompt
python axion.py

# One-shot mode — run a single command directly from your shell
python axion.py hash README.md
python axion.py dns google.com
python axion.py --help
```

## Features

**System**
- `sysinfo` — OS, CPU, RAM, disk, and GPU (NVIDIA) information
- `processes` — running process viewer, sorted by resource usage

**Network**
- `netinfo` — local network interfaces and IP information
- `dns <domain>` — DNS record lookups (A, AAAA, MX, TXT, NS)
- `connections` — active network connection monitor
- `portscan <target>` — TCP port scanner, **restricted to localhost and private (RFC 1918) IP ranges only** — enforced in code, not just by convention

**Security**
- `hash <filepath>` — MD5/SHA1/SHA256 file hashing with metadata
- `password` — password strength auditor (entropy + pattern-based, hidden input, never logged/stored)
- `baseline <dir> <name>` / `verify <name>` — file integrity monitor (create and compare SHA256 baselines)
- `logscan <filepath>` — log file analyzer for suspicious patterns and brute-force detection

**Intelligence**
- `ip [address]` — IP geolocation and ASN lookup (via ip-api.com)
- `cve <CVE-ID>` / `cve-search <keyword>` — vulnerability lookup via the NVD database

**Reporting & Alerts**
- Every tool can save results as timestamped JSON + HTML reports (`data/reports/`)
- Optional Discord webhook alerts for security-relevant findings (brute-force detection, integrity changes) — `config-webhook <url>` to set up

Run `help` inside the REPL (or `python axion.py --help`) for the full, always-current command list.

## Installation

Requires Python 3.13+.

```bash
git clone https://github.com/PlasmaLMAO/Axion-v2.git
cd AXION-V2
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Usage

```bash
# Launch the interactive REPL
python axion.py

axion> sysinfo
axion> hash README.md
axion> dns example.com
axion> cve CVE-2021-44228
axion> help
axion> exit
```

```bash
# Or run any command directly, one-shot
python axion.py sysinfo
python axion.py cve-search openssl
```

### Discord Webhook Alerts (optional)

To get notified when AXION detects something worth flagging (brute-force patterns, integrity violations):

1. In your Discord server: Server Settings → Integrations → Webhooks → New Webhook → Copy URL
2. `python axion.py config-webhook <your-webhook-url>`
3. `python axion.py config-test` to confirm it works

The webhook URL only allows AXION to *post* to that one channel — it cannot read messages, join servers, or access anything else.

## Architecture

```
Axion/
├── axion.py              # Entry point — REPL + one-shot CLI dispatch
├── core/                  # Framework: config, logging, database, theming, reports, webhooks
├── modules/
│   ├── system/            # OS/hardware info, process viewer
│   ├── network/            # Interfaces, DNS, connections, port scanner
│   ├── security/           # Hashing, passwords, integrity, log analysis
│   └── intelligence/       # IP lookup, CVE lookup
└── data/                   # Config, local database, generated reports (gitignored)
```

Every tool module is a standalone, independently testable class — `python -m modules.security.hashes` (etc.) works on its own outside the main app.

## Scope & Disclaimer

AXION V2 is built strictly for **defensive security, auditing your own systems, and learning**. The port scanner enforces localhost/private-IP-only scanning in code. No offensive, exploitation, or unauthorized-access tooling exists in this project, and none will be added. Use responsibly and only against systems and networks you own or have explicit authorization to test.

## License

[MIT](LICENSE)
