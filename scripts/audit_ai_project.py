#!/usr/bin/env python3
"""Audit AI project structure against the core standard."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, List

# Required directories for a compliant AI project
REQUIRED_DIRS: List[str] = [
    "config",
    "data",
    "data/raw",
    "data/processed",
    "data/prompts",
    "data/outputs",
    "data/cache",
    "data/embeddings",
    "docs",
]

# Required files for a compliant AI project
REQUIRED_FILES: List[str] = [
    "config/prompts.yaml",
    "config/models.yaml",
    "README.md",
]

# Optional/recommended items (warn if missing, but do not fail)
RECOMMENDED_FILES: List[str] = [
    ".gitignore",
    ".editorconfig",
    "docs/AI_PROMPTING_STANDARDS.md",
    "docs/COPILOT_USAGE.md",
]


@dataclass
class AuditResult:
    """Result of auditing a repo against the AI project structure standard."""

    target: str
    missing_dirs: list[str]
    missing_files: list[str]
    missing_recommended: list[str]
    config_validation_passed: bool | None = None

    @property
    def is_compliant(self) -> bool:
        """Return True if required directories/files exist."""
        return not self.missing_dirs and not self.missing_files

    def to_json(self) -> dict[str, object]:
        """Return a JSON-serializable representation of this result.

        Returns:
            A JSON-serializable dictionary representing this audit result.
        """
        payload: dict[str, object] = asdict(self)
        payload["is_compliant"] = self.is_compliant and (
            self.config_validation_passed in {True, None}
        )
        return payload


def _find_missing(root: Path, expected: Iterable[str]) -> list[str]:
    """Return any expected paths that do not exist under *root*.

    Args:
        root: Repository root to check.
        expected: Relative paths expected to exist.

    Returns:
        Relative paths that are missing under root.
    """
    missing: list[str] = []
    for rel_path in expected:
        if not (root / rel_path).exists():
            missing.append(rel_path)
    return missing


def audit(path: Path) -> AuditResult:
    """Audit *path* for required and recommended AI project structure items.

    Args:
        path: Target repository root.

    Returns:
        AuditResult describing missing required/recommended items.
    """
    missing_dirs = _find_missing(path, REQUIRED_DIRS)
    missing_files = _find_missing(path, REQUIRED_FILES)
    missing_recommended = _find_missing(path, RECOMMENDED_FILES)

    return AuditResult(
        target=str(path),
        missing_dirs=missing_dirs,
        missing_files=missing_files,
        missing_recommended=missing_recommended,
    )


def _run_config_validation(root: Path) -> bool:
    """Invoke the AJV validation script.

    Args:
        root: Repository root that contains scripts/ajv-validate.mjs.

    Returns:
        True if AJV validation succeeds; False otherwise.
    """
    script_path = root / "scripts" / "ajv-validate.mjs"
    if not script_path.exists():
        print("⚠️  Config validation skipped (scripts/ajv-validate.mjs not found).")
        return False

    result = subprocess.run(
        ["node", str(script_path)],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )

    if result.stdout:
        print(result.stdout.strip())
    if result.stderr:
        print(result.stderr.strip(), file=sys.stderr)

    return result.returncode == 0


def _print_block(title: str, items: Iterable[str]) -> bool:
    """Print a titled list block.

    Args:
        title: Block title.
        items: Iterable of items to print.

    Returns:
        True if any items were printed; False otherwise.
    """
    items = list(items)
    if not items:
        return False
    print(title)
    for item in items:
        print(f"  - {item}")
    return True


def print_human(result: AuditResult) -> None:
    """Print a human-readable audit report.

    Args:
        result: The audit result to render.
    """
    print(f"Auditing AI structure in: {result.target}\n")

    printed_any = _print_block("Missing required directories:", result.missing_dirs)
    if printed_any and result.missing_files:
        print()
    printed_any = _print_block("Missing required files:", result.missing_files) or printed_any
    if printed_any and result.missing_recommended:
        print()
    _print_block("Missing recommended items (not strictly required):", result.missing_recommended)

    if result.config_validation_passed is True:
        print("\n✅ Schema validation passed (AJV).")
    elif result.config_validation_passed is False:
        print("\n❌ Schema validation failed (see output above).")

    if result.is_compliant and (result.config_validation_passed in {True, None}):
        print("\n✅ Project matches core AI structure.")
    else:
        print("\n❌ Project does NOT match core AI structure.")
        print("Suggested fix: copy or adapt missing items from RZ-AI-Core-Standards/templates.")


def parse_args(argv: list[str]) -> argparse.Namespace:
    """Parse CLI arguments for the audit command.

    Args:
        argv: Raw argv list including program name.

    Returns:
        Parsed CLI arguments.
    """
    parser = argparse.ArgumentParser(
        description="Audit AI project structure against the core standard",
    )
    parser.add_argument(
        "path", nargs="?", default=".", help="Path to the target project (default: current dir)"
    )
    parser.add_argument(
        "--json", action="store_true", help="Emit JSON instead of human-readable output"
    )
    parser.add_argument(
        "--validate-configs",
        action="store_true",
        help="Run scripts/ajv-validate.mjs after structure audit",
    )
    return parser.parse_args(argv[1:])


def main(argv: list[str]) -> int:
    """CLI entry point.

    Args:
        argv: Raw argv list including program name.

    Returns:
        Process exit code.
    """
    args = parse_args(argv)

    target = Path(args.path).resolve()

    result = audit(target)

    if args.validate_configs:
        result.config_validation_passed = _run_config_validation(target)
        if result.config_validation_passed is False:
            result.missing_files.append("(schema validation failed)")

    if args.json:
        print(json.dumps(result.to_json(), indent=2))
    else:
        print_human(result)

    if not result.is_compliant:
        return 1
    if args.validate_configs and result.config_validation_passed is False:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
