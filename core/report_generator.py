import json
import sys
from pathlib import Path
from datetime import datetime
from html import escape

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.config import Config

ReportData = dict | list[dict]


class ReportGenerator:

    def __init__(self) -> None:
        self.config = Config()
        reports_dir = self.config.get("reports_path", "data/reports")
        self.reports_dir = PROJECT_ROOT / reports_dir
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def _timestamp_slug(self) -> str:
        """Return a filesystem-safe timestamp for use in filenames."""
        return datetime.now().strftime("%Y%m%d_%H%M%S")

    def _slugify(self, title: str) -> str:
        """Convert a report title into a safe filename fragment."""
        safe = "".join(c if c.isalnum() else "_" for c in title.lower())
        return safe.strip("_")[:50]

    def save_json(self, title: str, data: ReportData) -> Path:
        """Write a JSON report file. Returns the path written to."""
        filename = f"{self._slugify(title)}_{self._timestamp_slug()}.json"
        filepath = self.reports_dir / filename

        payload = {
            "title": title,
            "generated_at": datetime.now().isoformat(),
            "data": data,
        }

        with filepath.open("w", encoding="utf-8") as f:
            json.dump(payload, f, indent=4, default=str)

        return filepath

    def _render_rows(self, data: dict) -> str:
        """Render a single dict as HTML table rows."""
        rows = ""
        for key, value in data.items():
            rows += f"<tr><td>{escape(str(key))}</td><td>{escape(str(value))}</td></tr>\n"
        return rows

    def _render_html_body(self, title: str, data: ReportData) -> str:
        """Build the HTML body: one table for a dict, multiple for a list of dicts."""
        if isinstance(data, dict):
            return f"""
            <table>
                <thead><tr><th>Field</th><th>Value</th></tr></thead>
                <tbody>{self._render_rows(data)}</tbody>
            </table>
            """

        # list of dicts: one table section per entry
        sections = ""
        for i, entry in enumerate(data, start=1):
            sections += f"""
            <h2>Result {i}</h2>
            <table>
                <thead><tr><th>Field</th><th>Value</th></tr></thead>
                <tbody>{self._render_rows(entry)}</tbody>
            </table>
            """
        return sections

    def save_html(self, title: str, data: ReportData) -> Path:
        """Write an HTML report file. Returns the path written to."""
        filename = f"{self._slugify(title)}_{self._timestamp_slug()}.html"
        filepath = self.reports_dir / filename

        generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        body = self._render_html_body(title, data)

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>AXION V2 Report: {escape(title)}</title>
<style>
    body {{ background: #1a1a1a; color: #e6e6e6; font-family: monospace; padding: 2rem; }}
    h1 {{ color: #e6e6e6; border-bottom: 1px solid #444; padding-bottom: 0.5rem; }}
    h2 {{ color: #bfbfbf; margin-top: 2rem; }}
    .meta {{ color: #777; margin-bottom: 2rem; }}
    table {{ border-collapse: collapse; width: 100%; margin-bottom: 1rem; }}
    th, td {{ border: 1px solid #444; padding: 0.5rem 1rem; text-align: left; }}
    th {{ background: #262626; color: #999; }}
    td {{ color: #e6e6e6; }}
</style>
</head>
<body>
    <h1>AXION V2 — {escape(title)}</h1>
    <div class="meta">Generated: {generated_at}</div>
    {body}
</body>
</html>
"""

        with filepath.open("w", encoding="utf-8") as f:
            f.write(html)

        return filepath

    def save_both(self, title: str, data: ReportData) -> tuple[Path, Path]:
        """Convenience method: write both JSON and HTML reports at once."""
        json_path = self.save_json(title, data)
        html_path = self.save_html(title, data)
        return json_path, html_path


if __name__ == "__main__":
    # Quick standalone test with fake data
    sample_data = {
        "Hostname": "test-host",
        "OS": "Linux",
        "Uptime": "1:23:45",
    }
    gen = ReportGenerator()
    json_path, html_path = gen.save_both("Test Report", sample_data)
    print(f"JSON report: {json_path}")
    print(f"HTML report: {html_path}")
