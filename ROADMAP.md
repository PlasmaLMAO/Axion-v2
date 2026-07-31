# AXION V2 — Roadmap

Big-picture plan for expanding AXION V2. Ordered by priority; not a
strict sequence — we'll jump around as makes sense, but this is the
rough shape of what's next.

## Phase A — Polish / UX

The "make it feel alive" pass.

- [ ] **Live TUI dashboard mode** — a persistent full-screen view (à la
      `htop`/`glances`) showing CPU/RAM/network/active connections
      updating in real time, using `rich.live.Live`. Launched via a
      new `dashboard` command from the REPL.
- [ ] **Animated banner intro** — subtle typing/reveal effect on the
      gradient ASCII art at startup instead of an instant print.
- [ ] **Progress bars/spinners** for slower operations (CVE search,
      IP lookups, port scans) using `rich.progress` — right now these
      just hang silently while the request is in flight.
- [ ] **Command aliases** — e.g. `ps` → `processes`, `pw` → `password`,
      so frequent commands are faster to type.
- [ ] **Tab-completion** for command names in the REPL (via `prompt_toolkit`
      or similar) — currently no autocomplete at all.
- [ ] **Persistent command history** (up-arrow to recall previous
      commands across sessions, not just within one REPL run).
- [ ] **`clear` / `banner` commands** — redraw the screen or replay the
      intro without restarting the app.

## Phase B — More Tools

New commands/modules, still strictly defensive/educational.

- [ ] `whois <domain>` — WHOIS registration lookup
- [ ] `ping <host>` — basic reachability/latency check (localhost/private
      + explicitly-authorized public hosts only, matching portscan's
      scoping philosophy)
- [ ] `subdomains <domain>` — passive subdomain enumeration via public
      sources (e.g. crt.sh certificate transparency logs) — passive/
      read-only, no active brute-forcing
- [ ] `headers <url>` — HTTP security header analyzer (checks for
      HSTS, CSP, X-Frame-Options, etc. on a given URL)
- [ ] `ssl <domain>` — TLS/SSL certificate inspector (expiry, issuer,
      chain validity)
- [ ] `breach <email>` — check an email against known breach databases
      (via HaveIBeenPwned API or similar)
- [ ] `yara <filepath>` — basic YARA rule scanning against a file, for
      pattern-based malware *detection* (defensive use of YARA, not
      malware creation)
- [ ] `firewall` — inspect/report on local firewall rules (read-only)

## Phase C — Smarter Alerts

Wire webhook notifications into more of the existing toolset, and make
alerts more actionable.

- [ ] Port scanner: alert when scanning your own network finds an
      unexpectedly open port
- [ ] IP lookup: alert when a looked-up IP is flagged (e.g. known to be
      in a high-risk ASN/region — combine with an abuse/reputation API)
- [ ] CVE lookup: alert when a searched CVE is CRITICAL severity
- [ ] Alert severity levels configurable per-trigger (some people want
      every finding pinged, others only want CRITICAL)
- [ ] `config alerts` command — turn specific alert types on/off
      without editing code
- [ ] Rich embeds with more context (e.g. include a mini report link,
      timestamp, hostname of the machine that triggered it)

## Phase D — Infrastructure

The "under the hood" work that makes the project more solid/professional.

- [ ] **Auto-updater** — `update` command checks the GitHub repo's
      latest release/tag against the local `VERSION`, notifies if
      behind, optionally pulls + reinstalls
- [ ] **Automated tests** — `pytest` suite covering at least the core
      framework (config, database, report generator) and pure-logic
      modules (password entropy, hash correctness)
- [ ] **GitHub Actions CI** — run tests automatically on every push
- [ ] **True plugin system** — revisit `module_loader.py`'s dynamic
      discovery so third-party modules can be dropped into a
      `modules/plugins/` folder with zero `axion.py` edits
- [ ] **Config profiles** — support multiple named configs (e.g.
      different webhook targets for "home" vs "work" contexts)
- [ ] **Packaging** — make `axion.py` installable via `pip install -e .`
      with a proper `setup.py`/`pyproject.toml`, so it can be run as
      `axion` from anywhere instead of `python axion.py`

## Stretch Goals

- [ ] Optional local SQLite-backed CVE cache (avoid re-hitting NVD API
      for repeat lookups)
- [ ] Export reports to PDF, not just JSON/HTML
- [ ] Web dashboard companion (Flask/FastAPI, read-only view of recent
      reports) — bigger undertaking, only if the CLI tool outgrows itself
