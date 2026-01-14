from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class NavItem:
    title: str
    path: str


SECTION_RE = re.compile(r"^(chapters|appendices):\s*$")
TITLE_RE = re.compile(r"^\s*-\s*title:\s*(?P<value>.+?)\s*$")
PATH_RE = re.compile(r"^\s*path:\s*(?P<value>.+?)\s*$")


def unquote(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
        return value[1:-1]
    return value


def parse_navigation_yaml(text: str) -> dict[str, list[NavItem]]:
    data: dict[str, list[NavItem]] = {"chapters": [], "appendices": []}
    current_section: str | None = None
    pending_title: str | None = None

    for lineno, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        section_match = SECTION_RE.match(stripped)
        if section_match:
            current_section = section_match.group(1)
            pending_title = None
            continue

        if current_section is None:
            continue

        title_match = TITLE_RE.match(line)
        if title_match:
            pending_title = unquote(title_match.group("value"))
            continue

        path_match = PATH_RE.match(line)
        if path_match:
            if pending_title is None:
                raise ValueError(f"navigation.yml:{lineno}: path without title")
            data[current_section].append(
                NavItem(title=pending_title, path=unquote(path_match.group("value")))
            )
            pending_title = None
            continue

    if pending_title is not None:
        raise ValueError("navigation.yml: title without path at end of file")

    return data


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def extract_titles(items: Any, *, label: str) -> list[str]:
    if not isinstance(items, list):
        raise ValueError(f"book-config.json: structure.{label} must be a list")
    titles: list[str] = []
    for i, item in enumerate(items):
        if not isinstance(item, dict):
            raise ValueError(
                f"book-config.json: structure.{label}[{i}] must be an object"
            )
        title = item.get("title")
        if not isinstance(title, str) or not title:
            raise ValueError(
                f"book-config.json: structure.{label}[{i}].title must be a non-empty string"
            )
        titles.append(title)
    return titles


def compare_ordered_titles(
    *, label: str, book_titles: list[str], nav_titles: list[str]
) -> list[str]:
    errors: list[str] = []

    if len(book_titles) != len(nav_titles):
        errors.append(
            f"{label}: count mismatch (book-config={len(book_titles)}, navigation={len(nav_titles)})"
        )

    for i, (book_title, nav_title) in enumerate(zip(book_titles, nav_titles)):
        if book_title != nav_title:
            errors.append(
                f"{label}: title mismatch at index {i} (book-config={book_title!r}, navigation={nav_title!r})"
            )

    if len(book_titles) > len(nav_titles):
        errors.append(f"{label}: extra in book-config: {book_titles[len(nav_titles):]!r}")
    elif len(nav_titles) > len(book_titles):
        errors.append(f"{label}: extra in navigation: {nav_titles[len(book_titles):]!r}")

    return errors


def main() -> int:
    book_path = Path("book-config.json")
    nav_path = Path("docs/_data/navigation.yml")

    try:
        book = load_json(book_path)
        if not isinstance(book, dict):
            raise ValueError("book-config.json must be a JSON object")

        structure = book.get("structure")
        if not isinstance(structure, dict):
            raise ValueError("book-config.json: structure must be an object")

        book_chapters = extract_titles(structure.get("chapters"), label="chapters")
        book_appendices = extract_titles(structure.get("appendices"), label="appendices")

        nav = parse_navigation_yaml(nav_path.read_text(encoding="utf-8"))
        nav_chapters = [item.title for item in nav["chapters"]]
        nav_appendices = [item.title for item in nav["appendices"]]
    except ValueError as e:
        sys.stderr.write(f"{e}\n")
        return 1

    errors: list[str] = []
    errors.extend(
        compare_ordered_titles(
            label="chapters", book_titles=book_chapters, nav_titles=nav_chapters
        )
    )
    errors.extend(
        compare_ordered_titles(
            label="appendices", book_titles=book_appendices, nav_titles=nav_appendices
        )
    )

    if errors:
        sys.stderr.write("book-config.json <-> navigation.yml consistency check failed:\n")
        for e in errors:
            sys.stderr.write(f"- {e}\n")
        return 1

    print(
        f"OK: chapters={len(book_chapters)} appendices={len(book_appendices)} (titles+order match)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
