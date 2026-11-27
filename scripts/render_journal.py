"""Render a public journal index, using only intentionally published entries."""
from datetime import date
from pathlib import Path
import re
import textwrap
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape

def rows(root):
    result = []
    for p in root.glob("*.md"):
        try:
            day = date.fromisoformat(p.stem)
        except ValueError:
            continue
        if p.stem != day.isoformat():
            continue
        content = p.read_text(encoding="utf-8")
        heading = re.search(r"^##\s+(.+)$", content, re.M)
        label = heading.group(1).strip() if heading else "Engineering journal entry"
        label = textwrap.shorten(label, width=56, placeholder="…") or "Engineering journal entry"
        result.append((day.isoformat(), label))
    return sorted(result, reverse=True)

def render(entries):
    recent = entries[:3]
    height = 128 + 45 * len(recent)
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="960" height="{height}" viewBox="0 0 960 {height}" role="img" aria-labelledby="t d">',
        '<title id="t">Engineering journal pulse</title><desc id="d">Latest dated entries from the public engineering journal.</desc>',
        '<defs><linearGradient id="b" x2="1" y2="1"><stop stop-color="#0a1527"/><stop offset="1" stop-color="#221a42"/></linearGradient></defs>',
        f'<rect width="960" height="{height}" rx="18" fill="url(#b)"/><rect x="1" y="1" width="958" height="{height-2}" rx="17" fill="none" stroke="#53447d"/>',
        '<text x="32" y="32" font-family="monospace" font-size="14" fill="#61e2ef">ENGINEERING JOURNAL / RECENT ENTRIES</text>',
        f'<text x="928" y="32" text-anchor="end" font-family="monospace" font-size="14" fill="#c4a5ff">{len(entries)} dated entries</text>',
        '<text x="32" y="65" font-family="Arial,sans-serif" font-size="24" font-weight="700" fill="#eef6ff">Build. Verify. Document.</text>',
    ]
    for i, (day, title) in enumerate(recent):
        y = 82 + 45 * i
        parts += [f'<rect x="32" y="{y}" width="896" height="36" rx="8" fill="#151f37" stroke="#413660"/>',
                  f'<circle cx="49" cy="{y+18}" r="4" fill="#61e2ef"/>',
                  f'<text x="62" y="{y+23}" font-family="monospace" font-size="14" fill="#c4a5ff">{escape(day)}</text>',
                  f'<text x="210" y="{y+23}" font-family="Arial,sans-serif" font-size="16" fill="#eef6ff">{escape(title)}</text>']
    parts += [f'<text x="32" y="{height-20}" font-family="Arial,sans-serif" font-size="13" fill="#a8bbd7">Only published entries are counted. No private conversation or repository details are collected.</text>', '</svg>']
    return "".join(parts)

if __name__ == "__main__":
    ET.fromstring(render([]))
    ET.fromstring(render([("2026-11-27", "A & B < C")]))
    svg = render(rows(Path("journal/entries")))
    ET.fromstring(svg)
    Path("assets/journal-pulse.svg").write_text(svg, encoding="utf-8")
    print("Public journal SVG validated")
