"""Render a public-only activity snapshot. No private repo or event details are stored."""
import collections
import datetime as dt
import json
import os
import urllib.request
from xml.sax.saxutils import escape


def get_json(url):
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "parasaf1-profile-activity", "X-GitHub-Api-Version": "2022-11-28"}
    if os.environ.get("GH_TOKEN"):
        headers["Authorization"] = "Bearer " + os.environ["GH_TOKEN"]
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=30) as response:
        return json.load(response)


def render(events, today):
    start = today - dt.timedelta(days=27)
    days = [start + dt.timedelta(days=i) for i in range(28)]
    counts = collections.Counter()
    seen = set()
    for event in events:
        if not event.get("public") or event.get("id") in seen:
            continue
        seen.add(event.get("id"))
        day = dt.date.fromisoformat(event["created_at"][:10])
        if start <= day <= today:
            counts[day] += 1
    palette = ["#29263e", "#4b347d", "#7654bd", "#a38af6", "#61e2ef"]
    blocks = []
    for i, day in enumerate(days):
        n = counts[day]
        level = min(n, 4)
        x = 39 + i * 31.5
        blocks.append(f'<rect x="{x:.1f}" y="120" width="25" height="33" rx="4" fill="{palette[level]}"><title>{day.isoformat()}: {n} observed public events</title></rect>')
    total = sum(counts.values())
    active = sum(n > 0 for n in counts.values())
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="960" height="214" viewBox="0 0 960 214" role="img" aria-labelledby="title desc">
<title id="title">Public GitHub activity snapshot</title><desc id="desc">{total} observed public events across {active} days in the last 28 UTC days. Sample of up to 300 recent public events, not a full contribution history.</desc>
<rect width="960" height="214" rx="16" fill="#0b1728"/><rect x="1" y="1" width="958" height="212" rx="15" fill="none" stroke="#51457e"/>
<g font-family="monospace"><text x="39" y="34" fill="#67d9f2" font-size="13" letter-spacing="2">PUBLIC ACTIVITY / 28 DAYS</text><text x="921" y="34" fill="#98b8d1" text-anchor="end" font-size="12">UTC / {today.isoformat()}</text></g>
<g font-family="Arial,sans-serif"><text x="39" y="82" fill="#eef6ff" font-size="35" font-weight="700">{total}</text><text x="130" y="80" fill="#a4bfd3" font-size="16">observed public events</text><text x="550" y="82" fill="#eef6ff" font-size="35" font-weight="700">{active}</text><text x="615" y="80" fill="#a4bfd3" font-size="16">days with observed activity</text></g>
{''.join(blocks)}
<g font-family="monospace" font-size="11" fill="#9fb9cc"><text x="39" y="170">{start.isoformat()}</text><text x="921" y="170" text-anchor="end">{today.isoformat()}</text><text x="39" y="196">Sample: up to 300 recent public events; excludes private activity. Not a contribution total.</text></g></svg>'''


if __name__ == "__main__":
    events = []
    for page in range(1, 4):
        batch = get_json(f"https://api.github.com/users/parasaf1/events/public?per_page=100&page={page}")
        if not isinstance(batch, list):
            raise RuntimeError("Unexpected API response")
        events.extend(batch)
        if len(batch) < 100:
            break
    today = dt.datetime.now(dt.timezone.utc).date()
    with open("assets/activity.svg", "w", encoding="utf-8", newline="\n") as out:
        out.write(render(events, today))
