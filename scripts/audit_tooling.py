#!/usr/bin/env python3
"""Audit presence of core tooling configs (CI, lint, type, tests, pre-commit)."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, List


CI_SENTINEL = ".github/workflows/ci.yml"

REQUIRED_FILES: List[str] = [
    ".pre-commit-config.yaml",
    CI_SENTINEL,  # sentinel; any workflow satisfies
]

RUFF_PRIMARY = "ruff.toml"
RUFF_DOT = ".ruff.toml"

RECOMMENDED_FILES: List[str] = [
    "mypy.ini",
    "pytest.ini",
    RUFF_PRIMARY,
    RUFF_DOT,
]

# Recommended directories (non-blocking)
RECOMMENDED_DIRS: List[str] = [
    "tests",
]

# Language-specific required/recommended artifacts (minimal, non-exhaustive)
LANGUAGE_REQUIRED: dict[str, List[str]] = {
    "python": ["pyproject.toml"],
    "javascript": ["package.json"],
    "typescript": ["package.json", "tsconfig.json"],
    "c_cpp": [],
    "powershell": [],
    "shell": [],
}

LANGUAGE_RECOMMENDED: dict[str, List[str]] = {
    "python": ["mypy.ini", "pytest.ini", RUFF_PRIMARY, RUFF_DOT],
    "javascript": ["package-lock.json", "yarn.lock", "pnpm-lock.yaml", ".eslintrc.json", ".eslintrc.js", "eslint.config.js"],
    "typescript": ["tsconfig.json"],
    "c_cpp": ["CMakeLists.txt", "Makefile"],
    "powershell": ["PSScriptAnalyzerSettings.psd1"],
    "shell": [".shellcheckrc"],
}

# Alternative groups where any file in the group satisfies the requirement
LANGUAGE_REQUIRED_ALT_GROUPS: dict[str, List[set[str]]] = {
    "c_cpp": [{"CMakeLists.txt", "Makefile"}],
}


@dataclass
class ToolingAuditResult:
    target: str
    missing_required: list[str]
    missing_recommended: list[str]
    missing_recommended_dirs: list[str]

    @property
    def is_compliant(self) -> bool:
        return not self.missing_required

    def to_json(self) -> dict[str, object]:
        payload = asdict(self)
        payload["is_compliant"] = self.is_compliant
        return payload


def _find_missing(root: Path, expected: Iterable[str]) -> list[str]:
    missing: list[str] = []
    for rel in expected:
        if not (root / rel).exists():
            missing.append(rel)
    return missing


def _find_missing_dirs(root: Path, expected_dirs: Iterable[str]) -> list[str]:
    missing: list[str] = []
    for rel in expected_dirs:
        path = root / rel
        if not path.exists() or not path.is_dir():
            missing.append(rel)
    return missing


def _has_ci_workflow(root: Path) -> bool:
    workflows_dir = root / ".github" / "workflows"
    if not workflows_dir.exists():
        return False
    for candidate in workflows_dir.iterdir():
        if candidate.is_file() and candidate.suffix in {".yml", ".yaml"}:
            return True
    return False


def _detect_languages(root: Path, max_files: int = 2000) -> set[str]:
    exts_to_lang = {
        ".py": "python",
        ".ts": "typescript",
        ".tsx": "typescript",
        ".js": "javascript",
        ".c": "c_cpp",
        ".cc": "c_cpp",
        ".cpp": "c_cpp",
        ".cxx": "c_cpp",
        ".h": "c_cpp",
        ".hpp": "c_cpp",
        ".hxx": "c_cpp",
        ".ps1": "powershell",
        ".sh": "shell",
    }
    langs: set[str] = set()
    count = 0
    for path in root.rglob("*"):
        if path.is_dir():
            continue
        count += 1
        if count > max_files:
            break
        lang = exts_to_lang.get(path.suffix.lower())
        if lang:
            langs.add(lang)
    return langs


def _check_language_requirements(root: Path, langs: set[str]) -> tuple[list[str], dict[str, list[str]]]:
    missing_required: list[str] = []
    missing_by_lang: dict[str, list[str]] = {}

    for lang in langs:
        required = LANGUAGE_REQUIRED.get(lang, [])
        alt_groups = LANGUAGE_REQUIRED_ALT_GROUPS.get(lang, [])

        lang_missing = _find_missing(root, required)

        for group in alt_groups:
            if not any((root / candidate).exists() for candidate in group):
                lang_missing.extend(sorted(group))

        if lang_missing:
            missing_by_lang[lang] = sorted(set(lang_missing))
            missing_required.extend(lang_missing)

    return missing_required, missing_by_lang


def _check_language_recommended(root: Path, langs: set[str]) -> dict[str, list[str]]:
    missing_by_lang: dict[str, list[str]] = {}
    for lang in langs:
        rec = LANGUAGE_RECOMMENDED.get(lang, [])
        missing = _find_missing(root, rec)
        if lang == "python":
            missing = _normalize_missing_recommended(missing)
        if missing:
            missing_by_lang[lang] = missing
    return missing_by_lang


def _normalize_missing_recommended(missing_recommended: list[str]) -> list[str]:
    missing = set(missing_recommended)

    # Ruff config group: ruff.toml OR .ruff.toml counts as present if either exists
    ruff_group = {RUFF_PRIMARY, RUFF_DOT}
    ruff_missing = missing & ruff_group
    if len(ruff_missing) < len(ruff_group):  # at least one exists
        missing -= ruff_group

    return sorted(missing)


def audit(target_root: Path) -> ToolingAuditResult:
    missing_required = _find_missing(target_root, REQUIRED_FILES)

    # CI: any workflow YAML satisfies the sentinel requirement
    if CI_SENTINEL in missing_required and _has_ci_workflow(target_root):
        missing_required = [m for m in missing_required if m != CI_SENTINEL]

    langs = _detect_languages(target_root)
    lang_required_missing, _ = _check_language_requirements(target_root, langs)
    lang_recommended_by_lang = _check_language_recommended(target_root, langs)

    missing_required.extend(lang_required_missing)

    raw_missing_recommended = _find_missing(target_root, RECOMMENDED_FILES)
    missing_recommended = _normalize_missing_recommended(raw_missing_recommended)
    missing_recommended_dirs = _find_missing_dirs(target_root, RECOMMENDED_DIRS)

    # Merge language-specific recommended into flat list for backward compatibility
    for items in lang_recommended_by_lang.values():
        missing_recommended.extend(items)

    # Deduplicate while preserving order
    seen: set[str] = set()
    deduped: list[str] = []
    for item in missing_recommended:
        if item in seen:
            continue
        seen.add(item)
        deduped.append(item)
    missing_recommended = deduped

    return ToolingAuditResult(
        target=str(target_root),
        missing_required=missing_required,
        missing_recommended=missing_recommended,
        missing_recommended_dirs=missing_recommended_dirs,
    )


def print_human(result: ToolingAuditResult) -> None:
    print(f"Auditing tooling in: {result.target}\n")

    if result.missing_required:
        print("Missing required tooling files:")
        for item in result.missing_required:
            print(f"  - {item}")
        print()

    if result.missing_recommended:
        print("Missing recommended tooling files:")
        for item in result.missing_recommended:
            print(f"  - {item}")
        print()

    if result.missing_recommended_dirs:
        print("Missing recommended directories (e.g., tests):")
        for item in result.missing_recommended_dirs:
            print(f"  - {item}")
        print()

    if result.is_compliant:
        print("✅ Core tooling files present.")
    else:
        print("❌ Tooling audit failed. See findings above.")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit tooling and CI presence.")
    parser.add_argument("--target-root", type=Path, default=Path("."), help="Path to target repo root")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of human-readable output")
    parser.add_argument("--report", type=Path, help="Where to write the audit report (JSON)")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    target_root = args.target_root.resolve()

    result = audit(target_root)
    json_payload = json.dumps(result.to_json(), indent=2)

    if args.json:
        print(json_payload)
    else:
        print_human(result)

    if args.report:
        args.report.write_text(json_payload + "\n", encoding="utf-8")

    return 0 if result.is_compliant else 1


if __name__ == "__main__":
    raise SystemExit(main())
