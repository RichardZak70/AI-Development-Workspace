#!/usr/bin/env python3
"""Merge core/template/project prompt files with simple precedence rules.

Precedence (lowest → highest): core → template → project.
Later sources override earlier ones per prompt id.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Mapping, cast

import yaml


@dataclass
class MergeReport:
    """Result of merging prompt maps, including override provenance."""

    merged: Dict[str, Any]
    source_by_key: Dict[str, str]
    overrides: Dict[str, list[str]]  # key -> list of sources seen in order


def _load_yaml(path: Path, required: bool = False, label: str | None = None) -> Dict[str, Any]:
    """Load a YAML mapping with optional requirement enforcement.

    Args:
        path: YAML file path.
        required: If True, raise if the file does not exist.
        label: Optional label used in error messages.

    Returns:
        Parsed YAML mapping with keys normalized to strings.
    """
    label = label or str(path)

    if not path.exists():
        if required:
            raise FileNotFoundError(f"Missing required prompts file: {path}")
        print(f"⚠️  Optional prompts file not found, skipping: {path}", file=sys.stderr)
        return {}

    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise RuntimeError(f"Failed to read {label}: {exc}") from exc

    data = yaml.safe_load(raw)
    if data is None:
        return {}
    if not isinstance(data, Mapping):
        raise ValueError(f"Expected mapping at top level in {label}, got {type(data).__name__}")
    data_map = cast(Mapping[str, Any], data)
    result: Dict[str, Any] = {}
    for key, value in data_map.items():
        result[str(key)] = value
    return result


def merge_prompts(
    core: Dict[str, Any], template: Dict[str, Any], project: Dict[str, Any]
) -> MergeReport:
    """Merge prompts with precedence project > template > core.

    Args:
        core: Core prompt mapping.
        template: Template prompt mapping.
        project: Project prompt mapping.

    Returns:
        MergeReport containing merged prompts and provenance.
    """
    merged: Dict[str, Any] = {}
    source_by_key: Dict[str, str] = {}
    overrides: Dict[str, list[str]] = {}

    sources = [("core", core), ("template", template), ("project", project)]

    for source_name, mapping in sources:
        for key, value in mapping.items():
            if key in merged:
                prev_source = source_by_key[key]
                overrides.setdefault(key, [prev_source]).append(source_name)
            merged[key] = value
            source_by_key[key] = source_name

    return MergeReport(merged=merged, source_by_key=source_by_key, overrides=overrides)


def write_yaml(data: Dict[str, Any], path: Path) -> None:
    """Write YAML to *path*, creating parent directories as needed.

    Args:
        data: YAML-serializable mapping to write.
        path: Destination file path.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(data, sort_keys=True), encoding="utf-8")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse CLI arguments for prompt merging.

    Args:
        argv: Optional argv list.

    Returns:
        Parsed CLI arguments.
    """
    parser = argparse.ArgumentParser(
        prog="prompt_merge",
        description="Merge prompts with project > template > core precedence.",
    )
    parser.add_argument(
        "--core",
        type=Path,
        default=Path("config/prompts.core.yaml"),
        help="Path to core prompts.yaml (required)",
    )
    parser.add_argument(
        "--template",
        type=Path,
        default=Path("config/prompts.defaults.yaml"),
        help="Path to template prompts.defaults.yaml (optional)",
    )
    parser.add_argument(
        "--project",
        type=Path,
        default=Path("config/prompts.custom.yaml"),
        help="Path to project prompts.custom.yaml (optional)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("config/prompts.merged.yaml"),
        help="Output merged prompts path",
    )
    parser.add_argument("--dry-run", action="store_true", help="Do not write output; just report")
    parser.add_argument(
        "--show-overrides",
        action="store_true",
        help="Print which prompt IDs were overridden and source order",
    )
    return parser.parse_args(argv)


def _print_overrides(overrides: Dict[str, list[str]]) -> None:
    """Print overrides to stderr in a human-readable form.

    Args:
        overrides: Mapping of prompt id to list of sources encountered.
    """
    if not overrides:
        return
    print("Overrides detected (later source overrides earlier):", file=sys.stderr)
    for key, sources in sorted(overrides.items()):
        chain = " -> ".join(sources)
        print(f"  - {key}: {chain}", file=sys.stderr)
    print(file=sys.stderr)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point.

    Args:
        argv: Optional argv list.

    Returns:
        Process exit code.
    """
    args = parse_args(argv)

    try:
        core = _load_yaml(args.core, required=True, label="core prompts")
        template = _load_yaml(args.template, required=False, label="template prompts")
        project = _load_yaml(args.project, required=False, label="project prompts")
    except (FileNotFoundError, ValueError, RuntimeError) as exc:
        print(str(exc), file=sys.stderr)
        return 1

    report = merge_prompts(core, template, project)

    if args.show_overrides:
        _print_overrides(report.overrides)

    if args.dry_run:
        print(f"[dry-run] Would merge {len(report.merged)} prompt(s)")
    else:
        write_yaml(report.merged, args.output)
        print(f"Merged {len(report.merged)} prompt(s) → {args.output}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
