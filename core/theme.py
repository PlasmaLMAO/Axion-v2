from rich.text import Text

# Core monochrome palette: whites and grays only, for the
# "serious tool" look (Nmap/Sysinternals style) rather than a
# colorful toy interface.
THEME = {
    "primary": "#e6e6e6",      # main text, headers
    "secondary": "#bfbfbf",    # secondary/label text
    "muted": "#999999",        # dim/less important text
    "faint": "#777777",        # version numbers, timestamps
    "border": "#e6e6e6",       # panel/table borders

    # Semantic colors: desaturated, not neon, so they stay in
    # keeping with a professional monochrome tool rather than
    # clashing with it.
    "success": "#7fbf8f",      # muted green
    "warning": "#c9a86a",      # muted amber
    "error": "#c97a7a",        # muted red
    "info": "#7a9ec9",         # muted blue, for neutral notices
}

# Start and end colors for the ASCII art logo gradient: light gray
# at the top fading to a slightly dimmer gray at the bottom. Kept
# subtle and monochrome rather than a rainbow effect, to match the
# overall theme.
GRADIENT_START = "#f2f2f2"
GRADIENT_END = "#7a7a7a"


def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))


def _rgb_to_hex(rgb: tuple[int, int, int]) -> str:
    return "#{:02x}{:02x}{:02x}".format(*rgb)


def _interpolate(start: str, end: str, fraction: float) -> str:
    start_rgb = _hex_to_rgb(start)
    end_rgb = _hex_to_rgb(end)
    blended = tuple(
        round(start_rgb[i] + (end_rgb[i] - start_rgb[i]) * fraction)
        for i in range(3)
    )
    return _rgb_to_hex(blended)


def gradient_lines(
    text: str,
    start_color: str = GRADIENT_START,
    end_color: str = GRADIENT_END,
    bold: bool = True,
) -> Text:
    lines = text.split("\n")
    result = Text()
    line_count = max(len(lines) - 1, 1)  # avoid div-by-zero on single-line text

    for i, line in enumerate(lines):
        fraction = i / line_count
        color = _interpolate(start_color, end_color, fraction)
        style = f"bold {color}" if bold else color
        result.append(line, style=style)
        if i < len(lines) - 1:
            result.append("\n")

    return result
