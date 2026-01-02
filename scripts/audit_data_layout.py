#!/usr/bin/env python3
"""Audit data/ layout and output traceability for AI projects."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable, List, Mapping, cast

from jsonschema import Draft202012Validator, FormatChecker

REQUIRED_DIRS: list[str] = [
    "data",
    "data/raw",
    "data/processed",
    "data/prompts",
    "data/outputs",
    "data/cache",
    "data/embeddings",
]

# Derive allowed top-level subdirs in data/ from REQUIRED_DIRS to avoid duplication.
ALLOWED_TOP_LEVEL_IN_DATA: set[str] = {Path(p).name for p in REQUIRED_DIRS if p != "data"}

# Files that are allowed directly under data/ (common housekeeping)
ALLOWED_TOP_LEVEL_FILES_IN_DATA: set[str] = {".gitkeep", ".gitignore", "README.md"}

OUTPUT_METADATA_KEYS: list[str] = ["run_id", "model", "prompt_id", "timestamp"]
OUTPUT_SCHEMA_PATH: Path = (
    Path(__file__).resolve().parent.parent / "schemas" / "outputs_metadata.schema.json"
)


@dataclass
class DataAuditResult:
    """Result of checking data/ layout and output metadata traceability."""

    target: str
    missing_dirs: list[str]
    stray_items: list[str]
    metadata_issues: list[str]

    @property
    def is_compliant(self) -> bool:
        """Return True if required dirs exist and no issues were found."""
        return not self.missing_dirs and not self.stray_items and not self.metadata_issues

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


def _find_stray_items(data_root: Path) -> list[str]:
    """Find unexpected files/dirs directly under data/.

    Args:
        data_root: Path to the data/ directory to inspect.

    Returns:
        Relative paths of unexpected files/directories directly under data/.
    """
    stray: list[str] = []
    if not data_root.exists():
        return stray

    for child in data_root.iterdir():
        rel = str(child.relative_to(data_root.parent))  # e.g. "data/foo"
        name = child.name

        if child.is_dir():
            if name not in ALLOWED_TOP_LEVEL_IN_DATA:
                stray.append(rel)
        else:
            if name not in ALLOWED_TOP_LEVEL_FILES_IN_DATA:
                stray.append(rel)

    return stray


@lru_cache(maxsize=4)
def _load_output_schema(schema_path: Path) -> Mapping[str, object] | None:
    try:
        data = json.loads(schema_path.read_text(encoding="utf-8"))
    except OSError:
        return None
    if isinstance(data, Mapping):
        return cast(Mapping[str, object], data)
    return None


def _jsonschema_errors(schema: Mapping[str, object], data: Mapping[str, object]) -> List[str]:
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    data_obj: Any = data
    validator_any: Any = validator
    return [error.message for error in validator_any.iter_errors(data_obj)]


def _check_output_metadata(
    outputs_root: Path,
    max_files: int | None = None,
    schema_path: Path | None = None,
) -> List[str]:
    """Check JSON files under data/outputs for required metadata keys and schema compliance.

    Args:
        outputs_root: Root directory to scan for JSON outputs.
        max_files: Optional maximum number of JSON files to validate.
        schema_path: Optional path to a JSON Schema used for validation.

    Returns:
        A list of human-readable issues found during metadata validation.
    """
    if not outputs_root.exists():
        return []

    issues: list[str] = []
    schema = _load_output_schema(schema_path) if schema_path else None
    count = 0

    for path in outputs_root.rglob("*.json"):
        if max_files is not None and count >= max_files:
            issues.append(
                f"{outputs_root}: metadata check truncated at {max_files} files; "
                "consider running without --max-output-files for full coverage."
            )
            break

        count += 1
        issues.extend(_validate_output_file(path, schema))

    return issues


def _validate_output_file(path: Path, schema: Mapping[str, Any] | None) -> List[str]:
    file_issues: list[str] = []

    data_obj, parse_error = _read_json(path)
    if parse_error:
        file_issues.append(parse_error)
        return file_issues

    object_error = _ensure_mapping(path, data_obj)
    if object_error:
        file_issues.append(object_error)
        return file_issues

    data_map = cast(Mapping[str, Any], data_obj)

    if schema:
        schema_errors = _jsonschema_errors(schema, data_map)
        if schema_errors:
            file_issues.append(f"{path}: schema validation failed: {', '.join(schema_errors)}")
            return file_issues

    if "timestamp" in data_map:
        ts_value = data_map["timestamp"]
        try:
            # Accept trailing Z by normalizing to +00:00 for fromisoformat
            ts_normalized = (
                ts_value.replace("Z", "+00:00") if isinstance(ts_value, str) else str(ts_value)
            )
            datetime.fromisoformat(ts_normalized)
        except Exception as exc:  # noqa: BLE001
            file_issues.append(f"{path}: invalid timestamp format: {exc}")
            return file_issues

    missing = [key for key in OUTPUT_METADATA_KEYS if key not in data_map]
    if missing:
        file_issues.append(f"{path}: missing metadata keys: {', '.join(missing)}")

    return file_issues


def _read_json(path: Path) -> tuple[Mapping[str, Any] | object | None, str | None]:
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except Exception as exc:  # noqa: BLE001
        return None, f"{path}: failed to parse JSON ({exc})"


def _ensure_mapping(path: Path, data: object) -> str | None:
    if not isinstance(data, dict):
        return f"{path}: expected top-level JSON object with metadata"
    return None


def audit(
    target_root: Path,
    max_output_files: int | None = None,
    metadata_schema: Path | None = None,
) -> DataAuditResult:
    """Audit *target_root* for expected data folders and output metadata.

    Args:
        target_root: Target repository root.
        max_output_files: Optional maximum number of output JSON files to validate.
        metadata_schema: Optional path to an outputs metadata JSON schema.

    Returns:
        DataAuditResult describing missing folders and metadata issues.
    """
    missing_dirs = _find_missing(target_root, REQUIRED_DIRS)
    stray_items = _find_stray_items(target_root / "data")
    schema_path = metadata_schema or OUTPUT_SCHEMA_PATH
    metadata_issues = _check_output_metadata(
        target_root / "data" / "outputs",
        max_files=max_output_files,
        schema_path=schema_path,
    )
    return DataAuditResult(
        target=str(target_root),
        missing_dirs=missing_dirs,
        stray_items=stray_items,
        metadata_issues=metadata_issues,
    )


def print_human(result: DataAuditResult) -> None:
    """Print a human-readable data layout audit report.

    Args:
        result: The audit result to render.
    """
    print(f"Auditing data layout in: {result.target}\n")

    if result.missing_dirs:
        print("Missing required directories:")
        for item in result.missing_dirs:
            print(f"  - {item}")
        print()

    if result.stray_items:
        print("Unexpected files/directories directly under data/:")
        for item in result.stray_items:
            print(f"  - {item}")
        print()

    if result.metadata_issues:
        print("Output metadata issues (data/outputs/**/*.json):")
        for item in result.metadata_issues:
            print(f"  - {item}")
        print()

    if result.is_compliant:
        print("✅ Data layout and outputs look compliant.")
    else:
        print("❌ Data layout issues detected. See above for details.")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse CLI arguments for the data layout audit.

    Args:
        argv: Optional argv list (excluding program name is acceptable).

    Returns:
        Parsed CLI arguments.
    """
    parser = argparse.ArgumentParser(
        prog="audit_data_layout", description="Audit data layout and traceability."
    )
    parser.add_argument(
        "--target-root",
        type=Path,
        default=Path("."),
        help="Path to target repo root (default: current directory)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit JSON instead of human-readable output",
    )
    parser.add_argument(
        "--report",
        type=Path,
        help="Where to write the JSON audit report",
    )
    parser.add_argument(
        "--max-output-files",
        type=int,
        default=None,
        help="Max number of JSON files under data/outputs to scan (for huge repos)",
    )
    parser.add_argument(
        "--metadata-schema",
        type=Path,
        default=None,
        help="Path to outputs metadata JSON schema (default: schemas/outputs_metadata.schema.json)",
    )
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

    result = audit(
        target_root,
        max_output_files=args.max_output_files,
        metadata_schema=args.metadata_schema,
    )
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
