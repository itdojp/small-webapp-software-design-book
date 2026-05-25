from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import unquote


REPOSITORY = "itdojp/small-webapp-software-design-book"
CANONICAL_HOMEPAGE = "https://itdojp.github.io/small-webapp-software-design-book/"
REQUIRED_ASSETS = [
    "assets/css/main.css",
    "assets/css/syntax-highlighting.css",
    "assets/js/theme.js",
    "assets/js/search.js",
    "assets/js/code-copy-lightweight.js",
]


@dataclass(frozen=True)
class NavItem:
    title: str
    path: str


@dataclass(frozen=True)
class Page:
    path: Path
    permalink: str
    title: str | None


SECTION_RE = re.compile(r"^(chapters|appendices):\s*$")
TITLE_RE = re.compile(r"^\s*-\s*title:\s*(?P<value>.+?)\s*$")
PATH_RE = re.compile(r"^\s*path:\s*(?P<value>.+?)\s*$")
FRONT_MATTER_RE = re.compile(r"^---\r?\n(.*?)\r?\n---\r?\n", re.DOTALL)
SCALAR_RE = re.compile(r"^(?P<key>[A-Za-z0-9_-]+):\s*(?P<value>.*?)\s*$")


class CheckError(ValueError):
    pass


def unquote_scalar(value: Any) -> Any:
    if not isinstance(value, str):
        return value
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
        return value[1:-1]
    return value


def parse_scalar_block(text: str) -> dict[str, str]:
    data: dict[str, str] = {}
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or line[:1].isspace():
            continue
        match = SCALAR_RE.match(line)
        if not match:
            continue
        data[match.group("key")] = str(unquote_scalar(match.group("value")))
    return data


def parse_front_matter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    match = FRONT_MATTER_RE.match(text)
    if not match:
        return {}
    return parse_scalar_block(match.group(1))


def normalize_public_path(value: Any, *, source: str) -> str:
    if not isinstance(value, str):
        raise CheckError(f"{source}: path must be a string")
    path = value.strip()
    if not path:
        raise CheckError(f"{source}: path must not be empty")
    if path.startswith(("http://", "https://", "mailto:")):
        raise CheckError(f"{source}: external paths are not allowed: {path!r}")
    if "{{" in path or "}}" in path:
        raise CheckError(f"{source}: Liquid expressions are not allowed in canonical paths")
    if "#" in path or "?" in path:
        raise CheckError(f"{source}: path must not include query or fragment: {path!r}")
    if "\\" in path:
        raise CheckError(f"{source}: path must use forward slashes: {path!r}")
    if not path.startswith("/"):
        path = "/" + path
    decoded = unquote(path)
    parts = [part for part in decoded.split("/") if part]
    if any(part in (".", "..") for part in parts):
        raise CheckError(f"{source}: path traversal is not allowed: {path!r}")
    if "%2f" in path.lower() or "%5c" in path.lower():
        raise CheckError(f"{source}: encoded path separators are not allowed: {path!r}")
    lower = path.lower()
    if path != "/" and not lower.endswith((".md", ".html", ".htm", ".pdf", ".txt", "/")):
        path += "/"
    return path


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
            pending_title = str(unquote_scalar(title_match.group("value")))
            continue

        path_match = PATH_RE.match(line)
        if path_match:
            if pending_title is None:
                raise CheckError(f"navigation.yml:{lineno}: path without title")
            data[current_section].append(
                NavItem(
                    title=pending_title,
                    path=normalize_public_path(
                        unquote_scalar(path_match.group("value")),
                        source=f"navigation.yml:{lineno}",
                    ),
                )
            )
            pending_title = None
            continue

    if pending_title is not None:
        raise CheckError("navigation.yml: title without path at end of file")

    return data


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def require_str(mapping: dict[str, Any], key: str, *, source: str) -> str:
    value = mapping.get(key)
    if not isinstance(value, str) or not value.strip():
        raise CheckError(f"{source}.{key} must be a non-empty string")
    return value.strip()


def collect_structure_items(items: Any, *, label: str) -> list[NavItem]:
    if not isinstance(items, list):
        raise CheckError(f"book-config.json: structure.{label} must be a list")
    result: list[NavItem] = []
    for i, item in enumerate(items):
        source = f"book-config.json: structure.{label}[{i}]"
        if not isinstance(item, dict):
            raise CheckError(f"{source} must be an object")
        for key in ("id", "title", "description", "path"):
            require_str(item, key, source=source)
        result.append(
            NavItem(
                title=require_str(item, "title", source=source),
                path=normalize_public_path(item.get("path"), source=f"{source}.path"),
            )
        )
    return result


def compare_ordered_items(
    *, label: str, book_items: list[NavItem], nav_items: list[NavItem]
) -> list[str]:
    errors: list[str] = []

    if len(book_items) != len(nav_items):
        errors.append(
            f"{label}: count mismatch (book-config={len(book_items)}, navigation={len(nav_items)})"
        )

    for i, (book_item, nav_item) in enumerate(zip(book_items, nav_items)):
        if book_item.title != nav_item.title:
            errors.append(
                f"{label}: title mismatch at index {i} "
                f"(book-config={book_item.title!r}, navigation={nav_item.title!r})"
            )
        if book_item.path != nav_item.path:
            errors.append(
                f"{label}: path mismatch at index {i} "
                f"(book-config={book_item.path!r}, navigation={nav_item.path!r})"
            )

    if len(book_items) > len(nav_items):
        errors.append(f"{label}: extra in book-config: {book_items[len(nav_items):]!r}")
    elif len(nav_items) > len(book_items):
        errors.append(f"{label}: extra in navigation: {nav_items[len(book_items):]!r}")

    return errors


def find_duplicates(values: list[str]) -> list[str]:
    seen: set[str] = set()
    duplicates: list[str] = []
    for value in values:
        if value in seen and value not in duplicates:
            duplicates.append(value)
        seen.add(value)
    return duplicates


def collect_pages() -> list[Page]:
    candidates = [
        Path("docs/index.md"),
        *sorted(Path("docs/chapters").glob("*.md")),
        *sorted(Path("docs/appendix").glob("*.md")),
    ]
    pages: list[Page] = []
    for file_path in candidates:
        if not file_path.exists():
            continue
        fm = parse_front_matter(file_path)
        permalink = fm.get("permalink")
        if isinstance(permalink, str) and permalink.strip():
            pages.append(
                Page(
                    path=file_path,
                    permalink=normalize_public_path(
                        permalink, source=f"{file_path}:permalink"
                    ),
                    title=fm.get("title"),
                )
            )
    return pages


def validate_canonical_metadata(book: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    expected = {
        "title": "要件から始めるソフトウェア設計（小規模TS Webアプリの実践）",
        "description": "小〜中規模の TypeScript Web アプリを対象に、要件定義→設計→テストまでを一貫して学ぶ実践教材",
        "author": "株式会社アイティードゥ",
        "version": "0.1.0",
        "language": "ja",
        "license": "CC-BY-NC-SA-4.0",
        "homepage": CANONICAL_HOMEPAGE,
    }
    for key, expected_value in expected.items():
        actual = book.get(key)
        if actual != expected_value:
            errors.append(f"book-config.json: {key} must be {expected_value!r} (actual={actual!r})")

    repository = book.get("repository")
    if not isinstance(repository, dict):
        errors.append("book-config.json: repository must be an object")
    else:
        if repository.get("url") != f"https://github.com/{REPOSITORY}.git":
            errors.append("book-config.json: repository.url does not match canonical GitHub URL")
        if repository.get("branch") != "main":
            errors.append("book-config.json: repository.branch must be 'main'")

    config = parse_scalar_block(Path("docs/_config.yml").read_text(encoding="utf-8"))
    config_expected = {
        "title": expected["title"],
        "description": expected["description"],
        "author": expected["author"],
        "version": expected["version"],
        "lang": expected["language"],
        "license": expected["license"],
        "url": "https://itdojp.github.io",
        "baseurl": "/small-webapp-software-design-book",
        "repository": REPOSITORY,
        "homepage": CANONICAL_HOMEPAGE,
    }
    for key, expected_value in config_expected.items():
        actual = config.get(key)
        if actual != expected_value:
            errors.append(f"docs/_config.yml: {key} must be {expected_value!r} (actual={actual!r})")

    index_fm = parse_front_matter(Path("docs/index.md"))
    index_expected = {
        "title": expected["title"],
        "description": expected["description"],
        "author": expected["author"],
        "version": expected["version"],
        "permalink": "/",
    }
    for key, expected_value in index_expected.items():
        actual = index_fm.get(key)
        if actual != expected_value:
            errors.append(f"docs/index.md: front matter {key} must be {expected_value!r} (actual={actual!r})")

    return errors


def validate_pages_and_assets(all_items: list[NavItem]) -> list[str]:
    errors: list[str] = []
    pages = collect_pages()
    page_paths = [page.permalink for page in pages]
    nav_paths = [item.path for item in all_items]

    for dup in find_duplicates(page_paths):
        errors.append(f"duplicate permalink: {dup}")
    for dup in find_duplicates(nav_paths):
        errors.append(f"duplicate navigation/config path: {dup}")

    page_path_set = set(page_paths)
    for item in all_items:
        if item.path not in page_path_set:
            errors.append(f"configured path has no page permalink: {item.path}")

    listed_paths = set(nav_paths) | {"/"}
    for page in pages:
        if page.permalink not in listed_paths:
            errors.append(f"page permalink is not listed in navigation/book-config: {page.path} -> {page.permalink}")

    for page in pages:
        fm = parse_front_matter(page.path)
        for key in ("prev", "next"):
            target = fm.get(key)
            if isinstance(target, str) and target.strip():
                normalized = normalize_public_path(target, source=f"{page.path}:{key}")
                if normalized not in listed_paths:
                    errors.append(f"{page.path}: {key} -> {normalized} is not a configured public path")

    for asset in REQUIRED_ASSETS:
        path = Path("docs") / asset
        if not path.is_file() or path.stat().st_size == 0:
            errors.append(f"required public asset is missing or empty: docs/{asset}")

    return errors


def main() -> int:
    try:
        book = load_json(Path("book-config.json"))
        if not isinstance(book, dict):
            raise CheckError("book-config.json must be a JSON object")

        structure = book.get("structure")
        if not isinstance(structure, dict):
            raise CheckError("book-config.json: structure must be an object")

        book_chapters = collect_structure_items(structure.get("chapters"), label="chapters")
        book_appendices = collect_structure_items(structure.get("appendices"), label="appendices")
        nav = parse_navigation_yaml(Path("docs/_data/navigation.yml").read_text(encoding="utf-8"))
    except (CheckError, json.JSONDecodeError) as e:
        sys.stderr.write(f"{e}\n")
        return 1

    errors: list[str] = []
    errors.extend(validate_canonical_metadata(book))
    errors.extend(
        compare_ordered_items(
            label="chapters", book_items=book_chapters, nav_items=nav["chapters"]
        )
    )
    errors.extend(
        compare_ordered_items(
            label="appendices", book_items=book_appendices, nav_items=nav["appendices"]
        )
    )
    errors.extend(validate_pages_and_assets([*book_chapters, *book_appendices]))

    if errors:
        sys.stderr.write("book metadata/navigation consistency check failed:\n")
        for e in errors:
            sys.stderr.write(f"- {e}\n")
        return 1

    print(
        "OK: metadata, navigation, permalinks, and required assets match "
        f"(chapters={len(book_chapters)} appendices={len(book_appendices)})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
