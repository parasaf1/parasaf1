"""Generate calendar and statistics from GitHub's viewer-visible contribution counts."""
import datetime as dt
import json
import os
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from xml.sax.saxutils import escape

QUERY = """
query {
  user(login: "parasaf1") {
    repositories(privacy: PUBLIC, ownerAffiliations: OWNER) { totalCount }
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount } }
      }
    }
  }
}
"""
BG = "#0b1728"
PALETTE = ["#29263e", "#4b347d", "#7654bd", "#a38af6", "#61e2ef"]

def load():
    result = subprocess.run(["gh", "api", "graphql", "-f", "query=" + QUERY],
                            check=True, capture_output=True, text=True, timeout=45)
    payload = json.loads(result.stdout)
    if payload.get("errors") or not payload.get("data", {}).get("user"):
        raise RuntimeError("GitHub contribution query failed")
    user = payload["data"]["user"]
    calendar = user["contributionsCollection"]["contributionCalendar"]
    today = dt.datetime.now(dt.timezone.utc).date()
    dates = {}
    for week in calendar["weeks"]:
        for day in week["contributionDays"]:
            date = dt.date.fromisoformat(day["date"])
            count = day["contributionCount"]
            if type(count) is not int or count < 0 or date in dates:
                raise ValueError("Unexpected calendar data")
            if date <= today:
                dates[date] = count
    if not dates or len(dates) > 370:
        raise ValueError("Unexpected calendar coverage")
    return dates, user["repositories"]["totalCount"], today

def metrics(dates, today):
    first, last = min(dates), max(dates)
    run = best = 0
    day = first
    while day <= last:
        run = run + 1 if dates.get(day, 0) else 0
        best = max(best, run)
        day += dt.timedelta(days=1)
    current = 0
    day = today
    if not dates.get(day, 0):
        day -= dt.timedelta(days=1)
    while dates.get(day, 0):
        current += 1
        day -= dt.timedelta(days=1)
    return sum(dates.values()), sum(v > 0 for v in dates.values()), current, best

def header(title, desc, height):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="960" height="{height}" viewBox="0 0 960 {height}" role="img" aria-labelledby="t d">'
            f'<title id="t">{escape(title)}</title><desc id="d">{escape(desc)}</desc>'
            f'<rect width="960" height="{height}" rx="18" fill="{BG}"/><rect x="1" y="1" width="958" height="{height-2}" rx="17" fill="none" stroke="#51457e"/>')

def txt(x, y, value, size=16, color="#c8deef", weight="400", anchor="start"):
    return f'<text x="{x}" y="{y}" font-family="Arial,sans-serif" font-size="{size}" font-weight="{weight}" fill="{color}" text-anchor="{anchor}">{escape(str(value))}</text>'

def stats(dates, repos, today):
    total, active, streak, longest = metrics(dates, today)
    items = [("Contributions", total), ("Active days", active), ("Public repositories", repos),
             ("Current streak / days", streak), ("Longest streak / days", longest),
             ("Peak day", max(dates.values()))]
    parts = [header("GitHub contribution statistics", str(items), 260),
             txt(32, 36, "GITHUB / ENGINEERING MOMENTUM", 15, "#67d9f2", "700"),
             txt(928, 36, today.isoformat() + " UTC", 13, "#a4bfd3", anchor="end")]
    for i, (label, value) in enumerate(items):
        x, y = 32 + (i % 3) * 304, 54 + (i // 3) * 82
        parts.append(f'<rect x="{x}" y="{y}" width="288" height="72" rx="9" fill="#211e40" stroke="#53447d"/>')
        parts.extend([txt(x+14, y+25, label, 14, "#a4bfd3"), txt(x+14, y+58, value, 28, "#eef6ff", "700")])
    parts.append(txt(32, 243, "Visible calendar counts only; streaks computed within returned dates. Today may still be in progress.", 13, "#a4bfd3"))
    return "".join(parts) + "</svg>"

def calendar(dates, today):
    first, last = min(dates), max(dates)
    sunday = first - dt.timedelta(days=(first.weekday()+1)%7)
    parts = [header("Isometric contribution calendar", f"GitHub visible contribution counts from {first} to {last}.", 300),
             txt(32, 36, "CONTRIBUTION LANDSCAPE / ISOMETRIC", 15, "#67d9f2", "700"),
             txt(928, 36, f"{first} to {last}", 13, "#a4bfd3", anchor="end")]
    peak = max(dates.values()) or 1
    for date, count in sorted(dates.items(), key=lambda p: ((p[0]-sunday).days//7, (p[0]-sunday).days%7)):
        week, day = divmod((date-sunday).days, 7)
        x, y = 90 + week*15 - day*6, 105 + week*1.5 + day*12
        h = 0 if count == 0 else 5 + 38*(count/peak)**0.5
        level = 0 if count == 0 else min(4, 1+int(3*count/peak))
        color = PALETTE[level]
        top = y-h
        parts.append(f'<g><title>{date}: {count} contributions</title><path d="M{x} {top}l10 -4 6 7 -10 4z" fill="{color}" stroke="{BG}" stroke-width=".6"/>')
        if h:
            parts.append(f'<path d="M{x} {top}l6 7v{h}l-6 -7z" fill="#48316e"/><path d="M{x+6} {top+7}l10 -4v{h}l-10 4z" fill="{color}" opacity=".65"/>')
        parts.append("</g>")
    parts.extend([txt(32, 276, "Height and color encode daily contribution counts. Anonymous private totals may appear if publicly visible on GitHub.", 13, "#a4bfd3")])
    return "".join(parts) + "</svg>"

def self_test():
    day = dt.date(2026, 11, 27)
    sample = {day-dt.timedelta(days=i): n for i, n in enumerate([0, 2, 1, 0, 4, 1, 2])}
    assert metrics(sample, day) == (10, 5, 2, 3)
    assert metrics({day:0}, day) == (0,0,0,0)
    for value in [stats(sample, 2, day), calendar(sample, day)]:
        ET.fromstring(value)
    print("Contribution renderer self-test passed")

if __name__ == "__main__":
    self_test()
    if "--self-test" not in sys.argv:
        dates, repos, today = load()
        for name, svg in [("contribution-stats.svg", stats(dates, repos, today)), ("contribution-3d.svg", calendar(dates, today))]:
            ET.fromstring(svg)
            Path("assets", name).write_text(svg, encoding="utf-8")
