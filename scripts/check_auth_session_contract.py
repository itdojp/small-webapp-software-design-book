#!/usr/bin/env python3
"""Validate markers and selected rules in the auth/session documentation.

The check is intentionally dependency-free so the same contract runs locally and
in GitHub Actions. It protects cross-document B-17/D-25 references and selected
security boundaries from editorial regression; it does not validate an app's
runtime security or replace human review.
"""

from __future__ import annotations

import argparse
import re
import sys
from collections.abc import Mapping
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED: dict[str, tuple[str, ...]] = {
    "docs/index.md": (
        "Appendix B（B-17）",
        "Appendix D（D-25）",
    ),
    "docs/chapters/01-requirements-as-input.md": (
        "認証（Authentication）",
        "認可（Authorization）",
        "`unauthorized/401`",
        "`forbidden/403`",
        "Appendix B（B-17）",
    ),
    "docs/chapters/04-minimal-architecture-ts.md": (
        "sessionなし/無効/期限切れ/失効済みを`unauthorized/401`へ写像",
        "認証済みの権限不足`forbidden/403`と分ける",
        "認証成立後にusecaseが返すエラー",
        "B-17",
        "D-25",
    ),
    "docs/chapters/05-design-for-testability.md": (
        "未認証は `401`、認証済みの非管理者は `403`",
        "logout 後・期限切れ・失効後",
        "CSRF token が無効なら状態を変更しない",
        "Appendix B（B-17）",
        "Appendix D（D-25）",
    ),
    "docs/chapters/06-test-strategy-pyramid.md": (
        "未認証・期限切れ・失効済みの `401`",
        "認証済み権限不足の `403`",
        "idle/absolute timeout",
        "CSRF token と Origin",
        "Appendix B（B-17）",
        "Appendix D（D-25）",
    ),
    "docs/appendix/A-checklists.md": (
        "認証（主体確認）と認可（操作可否）が分離",
        "cookie session / bearer token",
        "`Secure` / `HttpOnly` / `SameSite`",
        "CSRF token と Origin/Referer",
        "idle timeout / absolute timeout",
        "logout時のserver-side invalidation",
        "セッションID、トークン",
    ),
    "docs/appendix/B-templates.md": (
        "## B-17. 認証・セッション契約テンプレ（任意）",
        "B-16, B-17",
        "- 認証失敗（未認証/無効/期限切れ/失効済み）:",
        "Authentication（主体確認）と Authorization（操作可否）",
        "<same-origin browser / same-site cross-origin browser / native / server-to-server>",
        "| 候補 | client側の保存 | 送信方法 | 主要脅威 | 適用条件/不採用理由 |",
        "server-managed session + opaque cookie",
        "bearer token",
        "`Secure` / `HttpOnly` / `SameSite`",
        "CSRF tokenとOrigin/Referer",
        "idle timeoutとabsolute timeout",
        "rotation、logout、失効",
        "`unauthorized/401`: 認証情報なし/無効/期限切れ/失効済み",
        "`forbidden/403`: 認証済みだが操作権限がない",
        "401 responseで対象resourceに適用するchallenge",
        "access token expiry/revocation境界",
        "| SESSION-1 | logout後に保護APIへアクセス |",
        "| SESSION-2 | idle/absolute timeout超過 |",
        "| SESSION-3 | 明示的な失効後 |",
        "| CSRF-1 | cookie方式でCSRF token/originが不正 |",
    ),
    "docs/appendix/C-references.md": (
        "OWASP ASVS 5.0.0",
        "Session_Management_Cheat_Sheet.html",
        "Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html",
        "REST_Security_Cheat_Sheet.html",
        "https://www.rfc-editor.org/rfc/rfc9110.html",
        "https://www.iana.org/assignments/http-authschemes/http-authschemes.xhtml",
        "https://www.rfc-editor.org/rfc/rfc6750.html",
        "https://www.rfc-editor.org/rfc/rfc9700.html",
        "確認日:",
    ),
    "docs/appendix/D-samples.md": (
        "| B-17 | D-25 |",
        "| R-8 | システムは有効な認証sessionを持つ利用者だけに保護機能へのアクセスを許可し、logout/期限切れ/失効後は拒否すること |",
        "| AC-8 | R-8 | sessionなし/無効/期限切れ/logout済み/失効済み |",
        "## D-25. 認証・セッション契約（記入例）（B-17）",
        "`__Host-session=<opaque-id>; Secure; HttpOnly; SameSite=Lax; Path=/`",
        "idle timeout: 最終の認証済みユーザー操作から30分（例）",
        "background polling、heartbeat、自動再読込はidle timeoutを延長しない",
        "absolute timeout: login成功から8時間（例）",
        "適用できる推奨値ではありません",
        "server-side recordを先に無効化",
        "`unauthorized/401`",
        "`forbidden/403`",
        "cookie session用の私的schemeを汎用例として固定せず",
        "| SESSION-1 | login→保護API成功→logout→同じcookieを再送 |",
        "| SESSION-2 | 最終活動時刻を固定してidle timeoutを1秒超過 |",
        "| SESSION-3 | login時刻を固定してabsolute timeoutを1秒超過 |",
        "| SESSION-4 | password変更/利用停止でsessionを失効後に再送 |",
        "| CSRF-1 | tokenなし/不一致、または許可外`Origin`で状態変更 |",
        "DB/outboxの非変更",
    ),
    "docs/appendix/E-glossary.md": (
        "認証（Authentication / AuthN）",
        "認可（Authorization / AuthZ）",
        "セッション（Session）",
        "CSRF（Cross-Site Request Forgery）",
        "`unauthorized/401`",
        "`forbidden/403`",
    ),
}

FORBIDDEN: dict[str, tuple[str, ...]] = {
    "docs/appendix/B-templates.md": (
        "- 認証/認可: (例) admin のみ（B-13参照）",
        "| forbidden | 403 | 認可失敗 | No | B-13 |",
    ),
    "docs/appendix/D-samples.md": (
        "- 認証/認可: 認証必須、認可は `admin` のみ",
        "| forbidden | 403 | 認可失敗（admin 以外） | No | D-18 |",
    ),
}

EXACT_ONCE: dict[str, tuple[str, ...]] = {
    "docs/appendix/B-templates.md": (
        "| unauthorized | 認証が必要です | 認証/セッション | 401 | No | code/相関IDを記録 | 秘密値を記録しない。B-17 |",
        "| unauthorized | 401 | 認証情報なし/無効/期限切れ/失効済み | No | B-17。対象resourceに適用する`WWW-Authenticate` challengeも契約化 |",
        "| forbidden | 403 | 認証済みだが認可失敗 | No | B-13 |",
    ),
    "docs/appendix/D-samples.md": (
        "| unauthorized | 認証が必要です | 認証/session | 401 | No | code/相関ID | session IDやcookie値を記録しない。D-25 |",
        "| unauthorized | 401 | sessionなし/無効/期限切れ/logout済み/失効済み | No | D-25 |",
        "| forbidden | 403 | 認証済みだが認可失敗（admin以外） | No | D-18 / D-21 |",
        "| csrf_rejected | 403 | CSRF tokenまたはrequest originが不正 | No | 認可失敗とcodeを分ける。D-25 |",
    ),
}

UNIQUE_HEADINGS: dict[str, tuple[str, ...]] = {
    "docs/appendix/B-templates.md": ("## B-17. 認証・セッション契約テンプレ（任意）",),
    "docs/appendix/D-samples.md": ("## D-25. 認証・セッション契約（記入例）（B-17）",),
}

LINK_CONTRACTS: dict[str, tuple[tuple[str, str], ...]] = {
    "docs/index.md": (
        ("B-17", "/appendix/B-templates/"),
        ("D-25", "/appendix/D-samples/"),
    ),
    "docs/chapters/01-requirements-as-input.md": (("B-17", "/appendix/B-templates/"),),
    "docs/chapters/04-minimal-architecture-ts.md": (
        ("B-17", "/appendix/B-templates/"),
        ("D-25", "/appendix/D-samples/"),
    ),
    "docs/chapters/05-design-for-testability.md": (
        ("B-17", "/appendix/B-templates/"),
        ("D-25", "/appendix/D-samples/"),
    ),
    "docs/chapters/06-test-strategy-pyramid.md": (
        ("B-17", "/appendix/B-templates/"),
        ("D-25", "/appendix/D-samples/"),
    ),
    "docs/appendix/E-glossary.md": (
        ("B-17", "/appendix/B-templates/"),
        ("D-25", "/appendix/D-samples/"),
    ),
}

CONTRADICTION_FIXTURES: tuple[str, ...] = (
    "認証情報が無い場合でも403を返してよい",
    "background pollingでもidle timeoutを毎回延長してよい",
)

CHECKED_DATE_RE = re.compile(r"^確認日: (?P<date>\d{4}-\d{2}-\d{2})(?:。|$)", re.MULTILINE)


def load_files(root: Path) -> dict[str, str]:
    files: dict[str, str] = {}
    for relative_path in REQUIRED:
        path = root / relative_path
        if not path.is_file():
            raise ValueError(f"missing contract file: {relative_path}")
        files[relative_path] = path.read_text(encoding="utf-8")
    return files


def validate(files: Mapping[str, str]) -> list[str]:
    errors: list[str] = []

    for relative_path, markers in REQUIRED.items():
        text = files.get(relative_path)
        if text is None:
            errors.append(f"{relative_path}: file not supplied")
            continue
        for marker in markers:
            if marker not in text:
                errors.append(f"{relative_path}: missing required marker {marker!r}")

    for relative_path, markers in FORBIDDEN.items():
        text = files.get(relative_path, "")
        for marker in markers:
            if marker in text:
                errors.append(f"{relative_path}: obsolete/ambiguous marker remains {marker!r}")

    for relative_path, headings in UNIQUE_HEADINGS.items():
        text = files.get(relative_path, "")
        for heading in headings:
            count = text.count(heading)
            if count != 1:
                errors.append(f"{relative_path}: heading {heading!r} must occur once (found {count})")

    for relative_path, markers in EXACT_ONCE.items():
        text = files.get(relative_path, "")
        for marker in markers:
            count = text.count(marker)
            if count != 1:
                errors.append(f"{relative_path}: contract row {marker!r} must occur once (found {count})")

    for relative_path, contracts in LINK_CONTRACTS.items():
        text = files.get(relative_path, "")
        for label, route in contracts:
            linked_lines = [line for line in text.splitlines() if label in line and "](" in line]
            if not linked_lines or any(route not in line for line in linked_lines):
                errors.append(f"{relative_path}: every linked {label} label must target {route}")

    references = files.get("docs/appendix/C-references.md", "")
    checked_dates = CHECKED_DATE_RE.findall(references)
    if len(checked_dates) != 1:
        errors.append(
            "docs/appendix/C-references.md: one ISO-8601 checked date is required "
            f"(found {len(checked_dates)})"
        )

    for relative_path, text in files.items():
        for lineno, line in enumerate(text.splitlines(), start=1):
            unauthenticated = any(
                token in line
                for token in ("未認証", "認証情報なし", "認証情報が無い", "認証情報がない", "sessionなし")
            )
            if unauthenticated and ("403" in line or "forbidden" in line) and "401" not in line:
                errors.append(
                    f"{relative_path}:{lineno}: unauthenticated credentials must not map to 403/forbidden"
                )

            background = any(token in line for token in ("background polling", "heartbeat", "自動再読込"))
            extends_idle = "idle" in line and any(token in line for token in ("延長", "更新"))
            rejects_extension = any(
                token in line for token in ("延長しない", "更新しない", "更新対象外", "対象外", "ならない", "禁止")
            )
            if background and extends_idle and not rejects_extension:
                errors.append(
                    f"{relative_path}:{lineno}: background traffic must not silently extend idle timeout"
                )

    return errors


def expect_rejected(files: dict[str, str], label: str) -> str | None:
    if validate(files):
        return None
    return f"negative self-test unexpectedly accepted: {label}"


def run_self_test(files: dict[str, str]) -> list[str]:
    errors: list[str] = []
    baseline_errors = validate(files)
    if baseline_errors:
        return ["baseline contract is invalid; self-test cannot start", *baseline_errors]

    cases = 0
    for relative_path, markers in REQUIRED.items():
        for marker in markers:
            mutated = dict(files)
            mutated[relative_path] = mutated[relative_path].replace(marker, "")
            error = expect_rejected(mutated, f"remove {relative_path}: {marker}")
            if error:
                errors.append(error)
            cases += 1

    for relative_path, markers in FORBIDDEN.items():
        for marker in markers:
            mutated = dict(files)
            mutated[relative_path] += f"\n{marker}\n"
            error = expect_rejected(mutated, f"inject obsolete {relative_path}: {marker}")
            if error:
                errors.append(error)
            cases += 1

    for relative_path, headings in UNIQUE_HEADINGS.items():
        for heading in headings:
            mutated = dict(files)
            mutated[relative_path] += f"\n{heading}\n"
            error = expect_rejected(mutated, f"duplicate {relative_path}: {heading}")
            if error:
                errors.append(error)
            cases += 1

    for relative_path, markers in EXACT_ONCE.items():
        for marker in markers:
            mutated = dict(files)
            mutated[relative_path] = mutated[relative_path].replace(marker, "")
            error = expect_rejected(mutated, f"remove contract row {relative_path}: {marker}")
            if error:
                errors.append(error)
            cases += 1

    for relative_path, contracts in LINK_CONTRACTS.items():
        for label, route in contracts:
            mutated = dict(files)
            lines = mutated[relative_path].splitlines(keepends=True)
            for index, line in enumerate(lines):
                if label in line and route in line:
                    lines[index] = line.replace(route, "/appendix/A-checklists/", 1)
                    break
            mutated[relative_path] = "".join(lines)
            error = expect_rejected(mutated, f"misroute {relative_path}: {label}")
            if error:
                errors.append(error)
            cases += 1

    references = "docs/appendix/C-references.md"
    mutated = dict(files)
    mutated[references] = CHECKED_DATE_RE.sub("確認日: 20-07-2026", mutated[references])
    error = expect_rejected(mutated, "malformed checked date")
    if error:
        errors.append(error)
    cases += 1

    for fixture in CONTRADICTION_FIXTURES:
        mutated = dict(files)
        target = "docs/appendix/D-samples.md"
        mutated[target] += f"\n{fixture}\n"
        error = expect_rejected(mutated, f"inject contradiction: {fixture}")
        if error:
            errors.append(error)
        cases += 1

    if not errors:
        print(f"auth/session documentation negative self-test OK ({cases} cases)")
    return errors


def print_errors(errors: list[str]) -> None:
    for error in errors:
        safe_error = error.replace("\r", " ").replace("\n", " ")
        print(f"::error::{safe_error}", file=sys.stderr)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true", help="run fail-closed mutation tests")
    args = parser.parse_args()

    try:
        files = load_files(ROOT)
    except (OSError, UnicodeError, ValueError) as exc:
        print_errors([str(exc)])
        return 1

    errors = run_self_test(files) if args.self_test else validate(files)
    if errors:
        print_errors(errors)
        return 1

    if not args.self_test:
        print(f"auth/session documentation markers OK ({len(REQUIRED)} files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
