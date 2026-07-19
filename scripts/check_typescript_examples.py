#!/usr/bin/env python3
"""Validate the contract between TypeScript fences and executable fixtures."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
import re
import tempfile


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
TYPESCRIPT_LANGUAGES = {"ts", "tsx", "typescript", "js", "jsx", "javascript"}
FENCE_RE = re.compile(
    r"^ {0,3}(`{3,}|~{3,})[ \t]*([A-Za-z0-9_+-]*)?(?:[ \t]+.*)?$"
)
MARKER_RE = re.compile(
    r"^<!-- code-example: (executable|excerpt|pseudocode)"
    r"(?: path=([A-Za-z0-9_./-]+))? -->$"
)
VISIBLE_LABELS = {
    "executable": "**分類: 実行可能例**",
    "excerpt": "**分類: 抜粋**",
    "pseudocode": "**分類: 疑似コード**",
}
FIXTURE_PREFIX = "examples/typescript/src/"


@dataclass(frozen=True)
class Problem:
    path: Path
    line: int
    message: str


@dataclass(frozen=True)
class Summary:
    executable: int = 0
    excerpt: int = 0
    pseudocode: int = 0

    @property
    def total(self) -> int:
        return self.executable + self.excerpt + self.pseudocode


def previous_nonblank(lines: list[str], index: int) -> int | None:
    while index >= 0:
        if lines[index].strip():
            return index
        index -= 1
    return None


def closing_fence(line: str, opener: str) -> bool:
    stripped = line.strip()
    return (
        stripped
        and set(stripped) == {opener[0]}
        and len(stripped) >= len(opener)
    )


def relative_display(path: Path, root: Path) -> Path:
    try:
        return path.relative_to(root)
    except ValueError:
        return path


def validate_repository(root: Path) -> tuple[list[Problem], Summary]:
    root = root.resolve()
    docs_dir = root / "docs"
    fixture_dir_unresolved = root / FIXTURE_PREFIX
    problems: list[Problem] = []
    counts = {"executable": 0, "excerpt": 0, "pseudocode": 0}
    referenced_fixtures: set[Path] = set()

    if not docs_dir.is_dir():
        return [Problem(Path("docs"), 1, "docs directory does not exist")], Summary()

    current = root
    for part in Path(FIXTURE_PREFIX).parts:
        current /= part
        if current.is_symlink():
            return [
                Problem(
                    relative_display(current, root),
                    1,
                    "fixture root and its ancestors must not contain symlinks",
                )
            ], Summary()
    fixture_dir = fixture_dir_unresolved.resolve()
    if root not in fixture_dir.parents:
        return [
            Problem(
                relative_display(fixture_dir_unresolved, root),
                1,
                "fixture root escapes repository root",
            )
        ], Summary()

    for doc in sorted(docs_dir.rglob("*.md")):
        lines = doc.read_text(encoding="utf-8").splitlines()
        index = 0
        while index < len(lines):
            opening = FENCE_RE.match(lines[index])
            if not opening:
                index += 1
                continue

            opener, language = opening.groups()
            closing_index = index + 1
            while closing_index < len(lines) and not closing_fence(
                lines[closing_index], opener
            ):
                closing_index += 1
            if closing_index >= len(lines):
                problems.append(
                    Problem(
                        relative_display(doc, root),
                        index + 1,
                        f"unclosed {language or 'plain'} code fence",
                    )
                )
                break

            if (language or "").lower() not in TYPESCRIPT_LANGUAGES:
                index = closing_index + 1
                continue

            display_doc = relative_display(doc, root)
            marker_index = previous_nonblank(lines, index - 1)
            marker_match = (
                MARKER_RE.match(lines[marker_index].strip())
                if marker_index is not None
                else None
            )
            if not marker_match:
                problems.append(
                    Problem(
                        display_doc,
                        index + 1,
                        "TypeScript-family fence has no code-example classification marker",
                    )
                )
                index = closing_index + 1
                continue

            classification, fixture_path_text = marker_match.groups()
            counts[classification] += 1
            label_index = previous_nonblank(lines, marker_index - 1)
            expected_label = VISIBLE_LABELS[classification]
            if label_index is None or expected_label not in lines[label_index]:
                problems.append(
                    Problem(
                        display_doc,
                        index + 1,
                        f"reader-visible label is missing; expected {expected_label}",
                    )
                )

            if classification != "executable":
                if fixture_path_text:
                    problems.append(
                        Problem(
                            display_doc,
                            index + 1,
                            f"{classification} example must not declare a fixture path",
                        )
                    )
                index = closing_index + 1
                continue

            if not fixture_path_text:
                problems.append(
                    Problem(
                        display_doc,
                        index + 1,
                        "executable example must declare a fixture path",
                    )
                )
                index = closing_index + 1
                continue
            if not fixture_path_text.startswith(FIXTURE_PREFIX):
                problems.append(
                    Problem(
                        display_doc,
                        index + 1,
                        f"fixture path must be under {FIXTURE_PREFIX}",
                    )
                )
                index = closing_index + 1
                continue
            fixture_relative = PurePosixPath(fixture_path_text)
            if ".." in fixture_relative.parts or fixture_relative.suffix != ".ts":
                problems.append(
                    Problem(
                        display_doc,
                        index + 1,
                        "fixture path must be a .ts file without parent traversal",
                    )
                )
                index = closing_index + 1
                continue

            fixture_path_unresolved = root / fixture_path_text
            current = root
            symlink_found = False
            for part in fixture_relative.parts:
                current /= part
                if current.is_symlink():
                    problems.append(
                        Problem(
                            display_doc,
                            index + 1,
                            f"fixture path must not contain symlinks: {fixture_path_text}",
                        )
                    )
                    symlink_found = True
                    break
            if symlink_found:
                index = closing_index + 1
                continue

            fixture_path = fixture_path_unresolved.resolve()
            if fixture_dir not in fixture_path.parents:
                problems.append(
                    Problem(display_doc, index + 1, "fixture path escapes fixture root")
                )
                index = closing_index + 1
                continue
            if fixture_path in referenced_fixtures:
                problems.append(
                    Problem(
                        display_doc,
                        index + 1,
                        f"fixture path is referenced more than once: {fixture_path_text}",
                    )
                )
                index = closing_index + 1
                continue
            referenced_fixtures.add(fixture_path)

            if not fixture_path.is_file():
                problems.append(
                    Problem(
                        display_doc,
                        index + 1,
                        f"fixture does not exist: {fixture_path_text}",
                    )
                )
                index = closing_index + 1
                continue

            documented_source = "\n".join(lines[index + 1 : closing_index]) + "\n"
            fixture_source = fixture_path.read_text(encoding="utf-8")
            if documented_source != fixture_source:
                problems.append(
                    Problem(
                        display_doc,
                        index + 1,
                        f"code fence differs from fixture: {fixture_path_text}",
                    )
                )

            index = closing_index + 1

    fixture_files = set(fixture_dir.rglob("*.ts")) if fixture_dir.is_dir() else set()
    for orphan in sorted(fixture_files - referenced_fixtures):
        problems.append(
            Problem(
                relative_display(orphan, root),
                1,
                "TypeScript fixture is not referenced by an executable documentation fence",
            )
        )

    summary = Summary(
        executable=counts["executable"],
        excerpt=counts["excerpt"],
        pseudocode=counts["pseudocode"],
    )
    if summary.total == 0:
        problems.append(Problem(Path("docs"), 1, "no TypeScript-family fences found"))
    return problems, summary


def write_self_test_repository(root: Path) -> None:
    doc = root / "docs" / "chapters" / "sample.md"
    fixture = root / "examples" / "typescript" / "src" / "sample.ts"
    doc.parent.mkdir(parents=True)
    fixture.parent.mkdir(parents=True)
    source = 'export const answer: number = 42;\n'
    fixture.write_text(source, encoding="utf-8")
    fence = "`" * 3
    doc.write_text(
        "\n".join(
            [
                "# Sample",
                "",
                "**分類: 実行可能例** — CIで型検査する例です。",
                "<!-- code-example: executable path=examples/typescript/src/sample.ts -->",
                f"{fence}ts",
                source.rstrip("\n"),
                fence,
                "",
            ]
        ),
        encoding="utf-8",
    )


def assert_problem(problems: list[Problem], fragment: str) -> None:
    if not any(fragment in problem.message for problem in problems):
        messages = "; ".join(problem.message for problem in problems) or "<none>"
        raise AssertionError(f"expected problem containing {fragment!r}; got {messages}")


def run_self_test() -> None:
    scratch = REPOSITORY_ROOT / ".codex-local" / "tmp"
    scratch.mkdir(parents=True, exist_ok=True)
    cases = 0

    def run_document_negative_case(
        expected: str, transform, *, remove_fixture: bool = False
    ) -> None:
        nonlocal cases
        with tempfile.TemporaryDirectory(dir=scratch) as directory:
            root = Path(directory)
            write_self_test_repository(root)
            doc = root / "docs" / "chapters" / "sample.md"
            doc.write_text(transform(doc.read_text(encoding="utf-8")), encoding="utf-8")
            if remove_fixture:
                (root / "examples" / "typescript" / "src" / "sample.ts").unlink()
            problems, _ = validate_repository(root)
            assert_problem(problems, expected)
            cases += 1

    with tempfile.TemporaryDirectory(dir=scratch) as directory:
        root = Path(directory)
        write_self_test_repository(root)
        problems, summary = validate_repository(root)
        assert not problems and summary.executable == 1
        cases += 1

        fixture = root / "examples" / "typescript" / "src" / "sample.ts"
        fixture.write_text("export const answer = 41;\n", encoding="utf-8")
        problems, _ = validate_repository(root)
        assert_problem(problems, "differs from fixture")
        cases += 1

    with tempfile.TemporaryDirectory(dir=scratch) as directory:
        root = Path(directory)
        write_self_test_repository(root)
        doc = root / "docs" / "chapters" / "sample.md"
        doc.write_text(
            doc.read_text(encoding="utf-8").replace(
                "<!-- code-example: executable path=examples/typescript/src/sample.ts -->\n",
                "",
            ),
            encoding="utf-8",
        )
        problems, _ = validate_repository(root)
        assert_problem(problems, "has no code-example classification marker")
        cases += 1

    with tempfile.TemporaryDirectory(dir=scratch) as directory:
        root = Path(directory)
        write_self_test_repository(root)
        doc = root / "docs" / "chapters" / "sample.md"
        doc.write_text(
            doc.read_text(encoding="utf-8").replace(
                "**分類: 実行可能例**", "**分類: 抜粋**"
            ),
            encoding="utf-8",
        )
        problems, _ = validate_repository(root)
        assert_problem(problems, "reader-visible label is missing")
        cases += 1

    with tempfile.TemporaryDirectory(dir=scratch) as directory:
        root = Path(directory)
        write_self_test_repository(root)
        doc = root / "docs" / "chapters" / "sample.md"
        doc.write_text(
            doc.read_text(encoding="utf-8").replace(
                "executable path=examples/typescript/src/sample.ts",
                "pseudocode path=examples/typescript/src/sample.ts",
            ).replace("**分類: 実行可能例**", "**分類: 疑似コード**"),
            encoding="utf-8",
        )
        problems, _ = validate_repository(root)
        assert_problem(problems, "pseudocode example must not declare a fixture path")
        cases += 1

    with tempfile.TemporaryDirectory(dir=scratch) as directory:
        root = Path(directory)
        write_self_test_repository(root)
        doc = root / "docs" / "chapters" / "sample.md"
        doc.write_text(
            doc.read_text(encoding="utf-8").replace(
                "examples/typescript/src/sample.ts",
                "examples/typescript/src/../../outside.ts",
            ),
            encoding="utf-8",
        )
        problems, _ = validate_repository(root)
        assert_problem(problems, "without parent traversal")
        cases += 1

    with tempfile.TemporaryDirectory(dir=scratch) as directory:
        root = Path(directory)
        write_self_test_repository(root)
        fixture = root / "examples" / "typescript" / "src" / "sample.ts"
        outside = root / "outside.ts"
        outside.write_text("export const leaked = true;\n", encoding="utf-8")
        fixture.unlink()
        fixture.symlink_to(outside)
        problems, _ = validate_repository(root)
        assert_problem(problems, "fixture path must not contain symlinks")
        cases += 1

    with tempfile.TemporaryDirectory(dir=scratch) as directory:
        root = Path(directory)
        write_self_test_repository(root)
        orphan = root / "examples" / "typescript" / "src" / "orphan.ts"
        orphan.write_text("export {};\n", encoding="utf-8")
        problems, _ = validate_repository(root)
        assert_problem(problems, "fixture is not referenced")
        cases += 1

    fence = "`" * 3
    run_document_negative_case(
        "unclosed ts code fence", lambda text: text.rsplit(fence, 1)[0]
    )
    run_document_negative_case(
        "executable example must declare a fixture path",
        lambda text: text.replace(
            "executable path=examples/typescript/src/sample.ts", "executable"
        ),
    )
    run_document_negative_case(
        f"fixture path must be under {FIXTURE_PREFIX}",
        lambda text: text.replace(
            "examples/typescript/src/sample.ts", "src/sample.ts"
        ),
    )
    duplicate = "\n".join(
        [
            "",
            "**分類: 実行可能例** — 重複参照です。",
            "<!-- code-example: executable path=examples/typescript/src/sample.ts -->",
            f"{fence}ts",
            "export const answer: number = 42;",
            fence,
            "",
        ]
    )
    run_document_negative_case(
        "fixture path is referenced more than once", lambda text: text + duplicate
    )
    run_document_negative_case(
        "fixture does not exist", lambda text: text, remove_fixture=True
    )
    run_document_negative_case(
        "no TypeScript-family fences found",
        lambda _text: "# Sample without code\n",
        remove_fixture=True,
    )

    print(f"OK: TypeScript example contract self-test passed ({cases} cases)")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--self-test", action="store_true", help="run contract-checker regression cases"
    )
    args = parser.parse_args()
    if args.self_test:
        run_self_test()
        return 0

    problems, summary = validate_repository(REPOSITORY_ROOT)
    for problem in problems:
        print(f"::error file={problem.path},line={problem.line}::{problem.message}")
    if problems:
        print(f"FAILED: TypeScript example contract has {len(problems)} problem(s)")
        return 1
    print(
        "OK: TypeScript example contract passed "
        f"(total={summary.total}, executable={summary.executable}, "
        f"excerpt={summary.excerpt}, pseudocode={summary.pseudocode})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
