"""Check local links, Markdown anchors and referenced image files in the public profile."""
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
LINK = re.compile(r'\]\(\s*<?([^\s<>)]+)>?(?:\s+["\x27][^"\x27]*["\x27])?\s*\)|\b(?:href|src)\s*=\s*["\x27]([^"\x27]+)["\x27]', re.I)
HEADING = re.compile(r'^#{1,6}\s+(.+?)\s*#*\s*$', re.M)

def anchors(text):
    used = set()
    for title in HEADING.findall(text):
        slug = re.sub(r'[^\w\s-]', '', title.lower()).replace(' ', '-')
        candidate = slug
        suffix = 1
        while candidate in used:
            candidate = f'{slug}-{suffix}'
            suffix += 1
        used.add(candidate)
    return used

def validate_image(path):
    ext = path.suffix.lower()
    if ext == ".svg":
        tree = ET.parse(path)
        if tree.getroot().tag != "{http://www.w3.org/2000/svg}svg":
            raise ValueError("not an SVG root")
    elif ext in {".jpg", ".jpeg", ".png", ".gif", ".webp"}:
        data = path.read_bytes()
        valid = {
            ".jpg": data.startswith(b"\xff\xd8") and data.endswith(b"\xff\xd9"),
            ".jpeg": data.startswith(b"\xff\xd8") and data.endswith(b"\xff\xd9"),
            ".png": data.startswith(b"\x89PNG\r\n\x1a\n"),
            ".gif": data[:6] in (b"GIF87a", b"GIF89a") and data.endswith(b";"),
            ".webp": data[:4] == b"RIFF" and data[8:12] == b"WEBP",
        }
        if not valid[ext]:
            raise ValueError("invalid image signature")
    else:
        return False
    return True

def check(root):
    errors = []
    checked_images = set()
    count = 0
    docs = sorted(root.rglob("*.md"))
    for source in docs:
        content = source.read_text(encoding="utf-8")
        # Ignore fenced code examples; validate inline Markdown and HTML links.
        content = re.sub(r'(?ms)^ {0,3}(?:\x60{3,}|~{3,}).*?^ {0,3}(?:\x60{3,}|~{3,})[ \t]*$', '', content)
        for match in LINK.finditer(content):
            value = match.group(1) or match.group(2)
            try:
                url = urlsplit(value)
                if url.scheme or url.netloc:
                    continue
                raw = unquote(url.path)
                target = ((root / raw.lstrip("/")) if raw.startswith("/") else (source.parent / raw if raw else source)).resolve()
                count += 1
                if not target.is_relative_to(root.resolve()):
                    raise ValueError("target outside repository")
                if not target.exists():
                    raise ValueError("target does not exist")
                if url.fragment and target.suffix.lower() == ".md":
                    if unquote(url.fragment) not in anchors(target.read_text(encoding="utf-8")):
                        raise ValueError("Markdown anchor missing")
                if target.is_file() and target not in checked_images and validate_image(target):
                    checked_images.add(target)
            except (ValueError, OSError, ET.ParseError) as exc:
                errors.append(f"{source.relative_to(root)}: {value}: {exc}")
    print(f"Checked {len(docs)} Markdown files, {count} local links, {len(checked_images)} image files")
    for err in errors:
        print(err, file=sys.stderr)
    return not errors

if __name__ == "__main__":
    sys.exit(0 if check(ROOT) else 1)
