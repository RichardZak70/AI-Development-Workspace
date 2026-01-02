#!/usr/bin/env python3
"""Migrate inline prompts from Python source files into a centralized YAML config.

Usage:
    python scripts/migrate_prompts_from_code.py path/to/project [--output prompts.yaml]

The script scans Python files for string literals that look like prompts
(multiline strings assigned to variables ending in _PROMPT, _TEMPLATE, etc.)
and writes them to a YAML file following the RZ AI Core Standards format.
"""

from __future__ import annotations

import argparse
import ast
import re
from pathlib import Path
from typing import Any, Dict, List, Tuple

import yaml

# ---------------------------------------------------------------------------
# Detection heuristics
# ---------------------------------------------------------------------------

PROMPT_VAR_PATTERN = re.compile(r"(?i)(prompt|template|system_msg|user_msg|instruction)$")


def looks_like_prompt_var(name: str) -> bool:
    """Return True if variable name suggests it holds a prompt.

    Args:
        name: Variable name to evaluate.

    Returns:
        True if the name likely indicates the variable holds a prompt.
    """
    return bool(PROMPT_VAR_PATTERN.search(name))


def _prompts_from_assign(node: ast.Assign) -> list[Tuple[str, str]]:
    results: list[Tuple[str, str]] = []
    for target in node.targets:
        if isinstance(target, ast.Name) and looks_like_prompt_var(target.id):
            value = _extract_string(node.value)
            if value:
                results.append((target.id, value))
    return results


def _prompts_from_annassign(node: ast.AnnAssign) -> list[Tuple[str, str]]:
    if not (isinstance(node.target, ast.Name) and node.value):
        return []
    if not looks_like_prompt_var(node.target.id):
        return []
    value = _extract_string(node.value)
    return [(node.target.id, value)] if value else []


def extract_prompts_from_source(source: str) -> List[Tuple[str, str]]:
    """Parse *source* and return list of (variable_name, string_value) tuples.

    Args:
        source: Python source code to parse.

    Returns:
        List of (variable_name, string_value) tuples extracted from assignments.
    """
    prompts: List[Tuple[str, str]] = []
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return prompts

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            prompts.extend(_prompts_from_assign(node))
        elif isinstance(node, ast.AnnAssign):
            prompts.extend(_prompts_from_annassign(node))
    return prompts


def _extract_string(node: ast.expr) -> str | None:
    """Return string content if *node* is a string constant, else None.

    Args:
        node: AST expression to inspect.

    Returns:
        String content if node is a string constant; otherwise None.
    """
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


# ---------------------------------------------------------------------------
# Scanning and output
# ---------------------------------------------------------------------------


def scan_directory(root: Path) -> Dict[str, Dict[str, str]]:
    """Walk *root* for .py files and collect prompts keyed by relative path.

    Args:
        root: Directory root to scan.

    Returns:
        Mapping of relative file path to extracted prompt variable mappings.
    """
    results: Dict[str, Dict[str, str]] = {}
    for py_file in root.rglob("*.py"):
        try:
            source = py_file.read_text(encoding="utf-8")
        except Exception:
            continue
        prompts = extract_prompts_from_source(source)
        if prompts:
            rel = py_file.relative_to(root).as_posix()
            results[rel] = dict(prompts)
    return results


def build_yaml_structure(raw: Dict[str, Dict[str, str]]) -> Dict[str, Any]:
    """Transform raw scan results into the RZ prompts.yaml structure.

    Args:
        raw: Raw scan output keyed by file with prompt variable name/value pairs.

    Returns:
        Dictionary representing a prompts YAML mapping.
    """
    output: Dict[str, Any] = {}
    for file_key, prompts in raw.items():
        for var_name, content in prompts.items():
            # Use variable name (lowercased) as key; dedupe via numbering if needed
            base_key = var_name.lower()
            key = base_key
            counter = 1
            while key in output:
                key = f"{base_key}_{counter}"
                counter += 1
            output[key] = {
                "description": "TODO: describe what this prompt is for",
                "system": content,
                "user_template": "# TODO: define user template",
                "_source_file": file_key,
                "_source_var": var_name,
            }
    return output


def write_yaml(data: Dict[str, Any], dest: Path) -> None:
    """Write *data* to *dest* as YAML.

    Args:
        data: YAML-serializable mapping to write.
        dest: Destination file path.
    """
    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open("w", encoding="utf-8", newline="\n") as f:
        yaml.safe_dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments for prompt migration.

    Returns:
        Parsed CLI arguments.
    """
    parser = argparse.ArgumentParser(
        prog="migrate_prompts_from_code",
        description="Extract inline prompts from Python code into a YAML config.",
    )
    parser.add_argument(
        "project",
        type=Path,
        help="Root directory to scan for Python files.",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=Path("config/prompts.yaml"),
        help="Destination YAML file (default: config/prompts.yaml relative to project).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print extracted prompts without writing file.",
    )
    return parser.parse_args()


def main() -> None:
    """Scan a project for inline prompts and write a prompts YAML file."""
    args = parse_args()
    root = args.project.resolve()

    if not root.is_dir():
        raise SystemExit(f"Project path is not a directory: {root}")

    print(f"Scanning {root} for inline prompts...")
    raw = scan_directory(root)

    if not raw:
        print("No prompts found.")
        return

    total = sum(len(v) for v in raw.values())
    print(f"Found {total} prompt(s) in {len(raw)} file(s).")

    data = build_yaml_structure(raw)

    if args.dry_run:
        print("\n--- Extracted prompts (dry run) ---")
        print(yaml.safe_dump(data, default_flow_style=False, sort_keys=False, allow_unicode=True))
        return

    dest = args.output if args.output.is_absolute() else root / args.output
    write_yaml(data, dest)
    print(f"Wrote prompts to {dest}")


if __name__ == "__main__":
    main()
