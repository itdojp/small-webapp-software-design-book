from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Page:
    path: Path
    permalink: str


FRONT_MATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)
MD_LINK_RE = re.compile(r"\[[^\]]*?\]\((.*?)\)")
LIQUID_RELATIVE_URL_RE = re.compile(
    r"""\{\{\s*['"](?P<path>/[^'"]*)['"]\s*\|\s*relative_url\s*\}\}"""
)


def parse_front_matter(text: str) -> dict[str, Any]:
    match = FRONT_MATTER_RE.match(text)
    if not match:
        return {}
    raw = match.group(1)
    data: dict[str, Any] = {}
    for line in raw.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip().strip('"').strip("'")
    return data


def collect_pages() -> list[Page]:
    base_dir = Path("docs")
    candidates = [
        base_dir / "index.md",
        *sorted((base_dir / "chapters").glob("*.md")),
        *sorted((base_dir / "appendix").glob("*.md")),
    ]
    pages: list[Page] = []
    for file_path in candidates:
        if not file_path.exists():
            continue
        fm = parse_front_matter(file_path.read_text(encoding="utf-8"))
        permalink = fm.get("permalink")
        if isinstance(permalink, str) and permalink:
            pages.append(Page(path=file_path, permalink=permalink))
    return pages


def is_internal_permalink_link(url: str) -> bool:
    if not url:
        return False
    if url.startswith("#"):
        return False
    if "://" in url:
        return False
    if url.startswith("mailto:"):
        return False
    return url.startswith("/")


def normalize_internal_path(url: str) -> str:
    # strip query/fragment
    url = url.split("#", 1)[0].split("?", 1)[0]
    return url


def extract_internal_links(markdown: str) -> set[str]:
    links: set[str] = set()

    for match in MD_LINK_RE.finditer(markdown):
        raw_url = match.group(1).strip()
        if raw_url.startswith("{{"):
            liquid = LIQUID_RELATIVE_URL_RE.search(raw_url)
            if liquid:
                links.add(normalize_internal_path(liquid.group("path")))
            continue
        if is_internal_permalink_link(raw_url):
            links.add(normalize_internal_path(raw_url))

    for liquid in LIQUID_RELATIVE_URL_RE.finditer(markdown):
        links.add(normalize_internal_path(liquid.group("path")))

    return links


def main() -> int:
    pages = collect_pages()
    permalink_to_page = {p.permalink: p for p in pages}

    errors: list[str] = []

    # uniqueness
    if len(permalink_to_page) != len(pages):
        seen: set[str] = set()
        for p in pages:
            if p.permalink in seen:
                errors.append(f"duplicate permalink: {p.permalink} ({p.path})")
            seen.add(p.permalink)

    for page in pages:
        text = page.path.read_text(encoding="utf-8")
        fm = parse_front_matter(text)
        for key in ("prev", "next"):
            target = fm.get(key)
            if isinstance(target, str) and target:
                if target not in permalink_to_page:
                    errors.append(f"{page.path}: {key} -> {target} not found")

        for link in sorted(extract_internal_links(text)):
            if link not in permalink_to_page:
                errors.append(f"{page.path}: internal link -> {link} not found")

    if errors:
        sys.stderr.write("Internal link check failed:\n")
        for e in errors:
            sys.stderr.write(f"- {e}\n")
        return 1

    print(f"OK: {len(pages)} pages, {len(permalink_to_page)} permalinks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
