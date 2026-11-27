"""Render public-only profile panels from sanitized engineering-showcase metadata."""
import json
import textwrap
import urllib.request
from datetime import datetime, timezone
from xml.sax.saxutils import escape

BASE = "https://raw.githubusercontent.com/parasaf1/engineering-showcase/main/data"
OUTPUT = "assets/project-signals.svg"


def fetch_json(url: str):
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "parasaf1-profile-panels",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def wrap_lines(text: str, width: int, max_lines: int):
    parts = textwrap.wrap(text, width=width)
    if len(parts) > max_lines:
        parts = parts[: max_lines - 1] + [parts[max_lines - 1].rstrip(" .") + "…"]
    return [escape(p) for p in parts]


def card(x, y, width, height, accent, label, name, status, milestone, summary, latest_date, latest_text, highlights_count):
    lines = wrap_lines(summary, 40, 3)
    milestone_lines = wrap_lines(milestone, 40, 3)
    latest_lines = wrap_lines(latest_text or "Awaiting next public update", 36, 2)
    out = []
    out.append(f'<g transform="translate({x},{y})">')
    out.append(f'<rect width="{width}" height="{height}" rx="18" fill="#0f1d30" stroke="#53447d" stroke-width="1.5"/>')
    out.append(f'<rect x="0" y="0" width="{width}" height="10" rx="18" fill="{accent}" opacity="0.9"/>')
    out.append(f'<text x="28" y="42" fill="{accent}" font-family="monospace" font-size="12" letter-spacing="2">{escape(label)}</text>')
    out.append(f'<text x="28" y="77" fill="#eef6ff" font-family="Arial,sans-serif" font-size="28" font-weight="700">{escape(name)}</text>')
    out.append(f'<text x="28" y="106" fill="#9fc4d7" font-family="Arial,sans-serif" font-size="14">{escape(status)}</text>')
    out.append(f'<text x="28" y="138" fill="#67d9f2" font-family="Arial,sans-serif" font-size="14" font-weight="700">Current milestone</text>')
    y0 = 160
    for ln in milestone_lines:
        out.append(f'<text x="28" y="{y0}" fill="#d9e9f5" font-family="Arial,sans-serif" font-size="15">{ln}</text>')
        y0 += 20
    out.append(f'<text x="28" y="228" fill="#67d9f2" font-family="Arial,sans-serif" font-size="14" font-weight="700">Public summary</text>')
    y1 = 250
    for ln in lines:
        out.append(f'<text x="28" y="{y1}" fill="#d9e9f5" font-family="Arial,sans-serif" font-size="15">{ln}</text>')
        y1 += 20
    out.append(f'<rect x="28" y="318" width="{width-56}" height="90" rx="12" fill="#0b1728" stroke="#413660"/>')
    out.append(f'<text x="44" y="342" fill="#67d9f2" font-family="monospace" font-size="11" letter-spacing="1.4">LATEST PUBLIC UPDATE</text>')
    if latest_date:
        out.append(f'<text x="{width-40}" y="341" fill="#93b2c8" font-family="monospace" font-size="11" text-anchor="end">{escape(latest_date)}</text>')
    y2 = 365
    for ln in latest_lines:
        out.append(f'<text x="44" y="{y2}" fill="#eef6ff" font-family="Arial,sans-serif" font-size="14">{ln}</text>')
        y2 += 18
    stat_y = height - 46
    out.append(f'<rect x="28" y="{stat_y}" width="140" height="30" rx="999" fill="#231d43" stroke="#413660"/>')
    out.append(f'<text x="98" y="{stat_y+20}" fill="#eef6ff" text-anchor="middle" font-family="Arial,sans-serif" font-size="13">{highlights_count} highlights</text>')
    out.append(f'<rect x="184" y="{stat_y}" width="170" height="30" rx="999" fill="#231d43" stroke="#413660"/>')
    out.append(f'<text x="269" y="{stat_y+20}" fill="#eef6ff" text-anchor="middle" font-family="Arial,sans-serif" font-size="13">sanitized public evidence</text>')
    out.append('</g>')
    return "".join(out)


def render(learnava, ai_company):
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    ex_up = (ai_company.get("recent_updates") or [{}])[0]
    le_up = (learnava.get("recent_updates") or [{}])[0]
    ex_card = card(
        34, 94, 438, 478, "#61e2ef", "PROJECT SIGNAL / 01", "AI Company",
        ai_company.get("status", "Active development"), ai_company.get("current_milestone", ""),
        ai_company.get("public_summary", ""), ex_up.get("date", ""), ex_up.get("text", ""), len(ai_company.get("highlights", []))
    )
    le_card = card(
        488, 94, 438, 478, "#b59aff", "PROJECT SIGNAL / 02", "LearnAva",
        learnava.get("status", "Active development"), learnava.get("current_milestone", ""),
        learnava.get("public_summary", ""), le_up.get("date", ""), le_up.get("text", ""), len(learnava.get("highlights", []))
    )
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="960" height="604" viewBox="0 0 960 604" role="img" aria-labelledby="title desc">
<title id="title">Public engineering signals</title>
<desc id="desc">Public engineering signals for AI Company and LearnAva based on sanitized metadata.</desc>
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0%" stop-color="#081321"/>
    <stop offset="100%" stop-color="#201b42"/>
  </linearGradient>
</defs>
<rect width="960" height="604" rx="24" fill="url(#bg)"/>
<rect x="1" y="1" width="958" height="602" rx="23" fill="none" stroke="#51457e"/>
<text x="34" y="42" fill="#67d9f2" font-family="monospace" font-size="13" letter-spacing="2">PUBLIC ENGINEERING SIGNALS</text>
<text x="34" y="69" fill="#eef6ff" font-family="Arial,sans-serif" font-size="24" font-weight="700">Selected verified public project context</text>
<text x="926" y="42" text-anchor="end" fill="#9bb7cb" font-family="monospace" font-size="12">UTC / {generated}</text>
<text x="34" y="86" fill="#9bb7cb" font-family="Arial,sans-serif" font-size="15">Built from the sanitized public metadata published in the engineering showcase.</text>
{ex_card}
{le_card}
</svg>'''


if __name__ == "__main__":
    learnava = fetch_json(f"{BASE}/lernava.json")
    ai_company = fetch_json(f"{BASE}/ai-company.json")
    svg = render(learnava, ai_company)
    with open(OUTPUT, "w", encoding="utf-8", newline="\n") as f:
        f.write(svg)
