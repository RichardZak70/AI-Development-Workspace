#!/usr/bin/env python3
"""Audit documentation presence and README linkage against AI core standards."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

REQUIRED_DOCS: list[str] = [
    "docs/PROJECT_STRUCTURE.md",
    "docs/AI_PROMPTING_STANDARDS.md",
    "docs/COPILOT_USAGE.md",
    "docs/DATA_ORGANIZATION.md",
    "docs/SCHEMAS_AND_VALIDATION.md",
    "docs/LINTING_AND_CI_STANDARDS.md",
    "docs/AI_PROJECT_REVIEW_CHECKLIST.md",
]

RECOMMENDED_DOCS: list[str] = [
    "docs/STATUS.md",
]


@dataclass
class DocsAuditResult:
    """Result of checking docs existence and README linkage."""

    target: str
    missing_required: list[str]
    missing_recommended: list[str]
    readme_missing: bool
    unlinked_required: list[str]

    @property
    def is_compliant(self) -> bool:
        """Return True if required docs exist and are linked from README.md."""
        return not self.missing_required and not self.readme_missing and not self.unlinked_required

    def to_json(self) -> dict[str, object]:
        """Return a JSON-serializable representation of this result.

        Returns:
            A JSON-serializable dictionary representing this audit result.
        """
        payload = asdict(self)
        payload["is_compliant"] = self.is_compliant
        return payload


def _find_missing(root: Path, expected: Iterable[str]) -> list[str]:
    missing: list[str] = []
    for rel in expected:
        if not (root / rel).exists():
            missing.append(rel)
    return missing


def _load_readme(root: Path) -> str | None:
    readme_path = root / "README.md"
    if not readme_path.exists():
        return None
    try:
        return readme_path.read_text(encoding="utf-8")
    except OSError:
        # Treat unreadable README as missing
        return None


def _find_unlinked(existing_required: Iterable[str], readme_text: str | None) -> list[str]:
    """Return required docs that exist but are not referenced in README.

    Args:
        existing_required: Iterable of required doc paths that exist on disk.
        readme_text: README contents, or None if README is missing/unreadable.

    Returns:
        Required doc paths that are not referenced in README.
    """
    if readme_text is None:
        # README missing is already signaled; avoid redundant noise
        return []
    text_lower = readme_text.lower()
    unlinked: list[str] = []
    for rel in existing_required:
        rel_lower = rel.lower()
        basename_lower = Path(rel).name.lower()
        if rel_lower not in text_lower and basename_lower not in text_lower:
            unlinked.append(rel)
    return unlinked


def audit(target_root: Path) -> DocsAuditResult:
    """Audit *target_root* for required docs and README linkage.

    Args:
        target_root: Target repository root.

    Returns:
        DocsAuditResult describing missing docs and README linkage issues.
    """
    missing_required = _find_missing(target_root, REQUIRED_DOCS)
    missing_recommended = _find_missing(target_root, RECOMMENDED_DOCS)
    readme_text = _load_readme(target_root)
    readme_missing = readme_text is None
    existing_required = [doc for doc in REQUIRED_DOCS if doc not in missing_required]
    unlinked_required = _find_unlinked(existing_required, readme_text)

    return DocsAuditResult(
        target=str(target_root),
        missing_required=missing_required,
        missing_recommended=missing_recommended,
        readme_missing=readme_missing,
        unlinked_required=unlinked_required,
    )


def print_human(result: DocsAuditResult) -> None:
    """Print a human-readable documentation audit report.

    Args:
        result: The audit result to render.
    """
    print(f"Auditing docs in: {result.target}\n")

    if result.readme_missing:
        print("❌ README.md is missing (cannot verify links to standards).\n")

    if result.missing_required:
        print("Missing required docs:")
        for item in result.missing_required:
            print(f"  - {item}")
        print()

    if result.missing_recommended:
        print("Missing recommended docs:")
        for item in result.missing_recommended:
            print(f"  - {item}")
        print()

    if not result.readme_missing and result.unlinked_required:
        print("Required docs not referenced in README.md:")
        for item in result.unlinked_required:
            print(f"  - {item}")
        print()

    if result.is_compliant:
        print("✅ Docs present and referenced from README.md.")
    else:
        print("❌ Docs audit failed. See findings above.")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse CLI arguments for the docs audit.

    Args:
        argv: Optional argv list.

    Returns:
        Parsed CLI arguments.
    """
    parser = argparse.ArgumentParser(
        prog="audit_docs", description="Audit documentation against standards."
    )
    parser.add_argument(
        "--target-root", type=Path, default=Path("."), help="Path to target repo root"
    )
    parser.add_argument(
        "--json", action="store_true", help="Emit JSON instead of human-readable output"
    )
    parser.add_argument("--report", type=Path, help="Where to write the audit report (JSON)")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point.

    Args:
        argv: Optional argv list.

    Returns:
        Process exit code.
    """
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
