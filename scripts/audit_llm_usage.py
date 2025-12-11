#!/usr/bin/env python3
"""Audit LLM usage for raw provider calls and missing standardization."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Sequence


# File types to scan
SCAN_EXTENSIONS: set[str] = {".py", ".ts", ".tsx", ".js"}

# Directories to skip entirely
IGNORE_DIRS: set[str] = {
    ".git",
    ".hg",
    ".svn",
    "__pycache__",
    "node_modules",
    "dist",
    "build",
    "venv",
    ".venv",
}

# Simple substring patterns indicating raw provider usage
RAW_LLM_PATTERNS: list[tuple[str, str]] = [
    ("openai.ChatCompletion.create", "Raw OpenAI ChatCompletion call; use standard client abstraction."),
    ("openai.Completion.create", "Raw OpenAI Completion call; use standard client abstraction."),
    ("client.chat.completions.create", "Raw Azure OpenAI chat call; use standard client abstraction."),
    ("client.completions.create", "Raw Azure OpenAI completion call; use standard client abstraction."),
]


@dataclass
class Finding:
    path: str
    line: int
    message: str
    snippet: str | None = None

    def to_json(self) -> dict[str, object]:
        return asdict(self)


@dataclass
class LlmAuditResult:
    target: str
    findings: list[Finding]

    @property
    def is_compliant(self) -> bool:
        return not self.findings

    def to_json(self) -> dict[str, object]:
        return {
            "target": self.target,
            "findings": [f.to_json() for f in self.findings],
            "is_compliant": self.is_compliant,
        }


def _iter_code_files(root: Path) -> Iterable[Path]:
    """Yield code files under root, skipping ignored directories."""
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix not in SCAN_EXTENSIONS:
            continue
        if any(part in IGNORE_DIRS for part in path.parts):
            continue
        yield path


def _scan_file(
    path: Path,
    patterns: Sequence[tuple[str, str]],
    max_size_bytes: int | None,
) -> list[Finding]:
    findings: list[Finding] = []
    path_str = path.as_posix()

    try:
        if max_size_bytes is not None and path.stat().st_size > max_size_bytes:
            return findings
    except OSError:
        findings.append(
            Finding(path=path_str, line=0, message="Unable to stat file for scanning.", snippet=None)
        )
        return findings

    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        findings.append(
            Finding(path=path_str, line=0, message="Unable to read file for scanning.", snippet=None)
        )
        return findings

    lines = text.splitlines()
    lowered_lines = [line.lower() for line in lines]

    for lineno, (line_orig, line_lower) in enumerate(zip(lines, lowered_lines), start=1):
        for pattern, message in patterns:
            if pattern.lower() in line_lower:
                snippet = line_orig.strip()
                if len(snippet) > 160:
                    snippet = snippet[:157] + "..."
                findings.append(
                    Finding(path=path_str, line=lineno, message=message, snippet=snippet or None)
                )
    return findings


def audit(target_root: Path, max_size_bytes: int | None = 1_000_000) -> LlmAuditResult:
    findings: list[Finding] = []
    for file_path in _iter_code_files(target_root):
        findings.extend(_scan_file(file_path, RAW_LLM_PATTERNS, max_size_bytes=max_size_bytes))
    return LlmAuditResult(target=str(target_root), findings=findings)


def print_human(result: LlmAuditResult) -> None:
    print(f"Auditing LLM usage in: {result.target}\n")

    if not result.findings:
        print("✅ No raw LLM calls detected; usage appears standardized.")
    else:
        print("❌ Raw LLM usage detected:")
        for finding in result.findings:
            location = f"{finding.path}:{finding.line}" if finding.line else finding.path
            print(f"  - {location}: {finding.message}")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit LLM usage for standardized client and prompt handling.")
    parser.add_argument("--target-root", type=Path, default=Path("."), help="Path to target repo root")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of human-readable output")
    parser.add_argument("--report", type=Path, help="Where to write the audit report (JSON)")
    parser.add_argument(
        "--max-size-bytes",
        type=int,
        default=1_000_000,
        help="Maximum file size to scan (bytes); larger files are skipped. Use 0 to disable.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    target_root = args.target_root.resolve()

    max_size = None if args.max_size_bytes == 0 else args.max_size_bytes
    result = audit(target_root, max_size_bytes=max_size)
    payload = json.dumps(result.to_json(), indent=2)

    if args.json:
        print(payload)
    else:
        print_human(result)

    if args.report:
        args.report.write_text(payload + "\n", encoding="utf-8")

    return 0 if result.is_compliant else 1


if __name__ == "__main__":
    raise SystemExit(main())
