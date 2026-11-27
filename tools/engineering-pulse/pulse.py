"""Engineering Pulse: render deliberately public project summaries as a local SVG."""
import argparse
import json
from pathlib import Path
import textwrap
from xml.sax.saxutils import escape

THEMES = {
    "neon": ("#0b1728", "#211b40", "#61e2ef", "#c4a5ff", "#eef6ff", "#a8bbd7"),
    "slate": ("#101820", "#23323d", "#80d9ce", "#9ebcdb", "#f2f7fa", "#bac7d1"),
}
REQUIRED = {"name", "status", "milestone"}
ALLOWED = REQUIRED | {"summary"}

def validate(data):
    if not isinstance(data, dict) or set(data) != {"projects"}:
        raise ValueError("Expected one projects array")
    projects = data["projects"]
    if not isinstance(projects, list) or not 1 <= len(projects) <= 12:
        raise ValueError("Provide 1–12 projects")
    for p in projects:
        if not isinstance(p, dict) or not REQUIRED <= set(p) <= ALLOWED:
            raise ValueError("Only name, status, milestone and optional summary are allowed")
        for key, limit in [("name", 48), ("status", 48), ("milestone", 140), ("summary", 220)]:
            if key in p:
                v = p[key]
                if not isinstance(v, str) or not v.strip() or len(v) > limit:
                    raise ValueError(f"Invalid {key}; expected 1–{limit} characters")
                if any(ord(c) < 32 or 0xD800 <= ord(c) <= 0xDFFF or ord(c) in (0xFFFE, 0xFFFF) for c in v):
                    raise ValueError(f"Invalid XML character in {key}")
    return projects

def render(data, theme="neon"):
    projects = validate(data)
    if theme not in THEMES:
        raise ValueError("Unknown theme")
    bg, card, cyan, violet, fg, muted = THEMES[theme]
    width, height = 960, 100 + len(projects) * 224
    def txt(x, y, value, size, color, weight="400"):
        return f'<text x="{x}" y="{y}" font-family="Arial,sans-serif" font-size="{size}" font-weight="{weight}" fill="{color}">{escape(value)}</text>'
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        '<title id="title">Engineering Pulse</title><desc id="desc">Project status and milestones from supplied public metadata.</desc>',
        f'<rect width="{width}" height="{height}" rx="18" fill="{bg}"/>',
        txt(32, 38, "ENGINEERING PULSE", 15, cyan, "700"),
        txt(32, 68, "Selected public project milestones", 24, fg, "700")
    ]
    for i, p in enumerate(projects):
        y = 86 + i * 224
        parts.append(f'<rect x="24" y="{y}" width="912" height="210" rx="12" fill="{card}"/>')
        parts.append(txt(44, y+31, p["name"], 23, fg, "700"))
        parts.append(txt(44, y+57, "STATUS / " + p["status"], 15, violet))
        parts.append(txt(44, y+83, "MILESTONE", 12, cyan, "700"))
        for j, line in enumerate(textwrap.wrap(p["milestone"], width=72)):
            parts.append(txt(44, y+105+j*19, line, 15, fg))
        for j, line in enumerate(textwrap.wrap(p.get("summary", ""), width=78)):
            parts.append(txt(44, y+154+j*16, line, 13, muted))
    parts.append("</svg>")
    return "\n".join(parts)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="Explicitly approved public JSON")
    parser.add_argument("output", type=Path, help="Destination SVG")
    parser.add_argument("--theme", choices=THEMES, default="neon")
    args = parser.parse_args()
    try:
        svg = render(json.loads(args.input.read_text(encoding="utf-8")), args.theme)
        args.output.write_text(svg, encoding="utf-8")
    except (ValueError, OSError) as exc:
        parser.exit(2, f"Engineering Pulse: {exc}\n")

if __name__ == "__main__":
    main()
