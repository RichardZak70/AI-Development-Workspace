#!/usr/bin/env python3
"""Extract inline prompts from source files into a structured report."""

from __future__ import annotations

import argparse
import ast
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Sequence

PROMPT_VAR_PATTERN: tuple[str, ...] = (
    "prompt",
    "template",
    "system_msg",
    "user_msg",
    "instruction",
    "system_prompt",
    "user_prompt",
)

IGNORE_DIRS: set[str] = {
    ".git",
    ".hg",
    ".svn",
    "__pycache__",
    "venv",
    ".venv",
}


@dataclass
class PromptFinding:
    """A single extracted prompt occurrence from source code."""

    path: str  # path relative to target root
    line: int  # line number of the assignment
    var_name: str
    value: str

    def to_json(self) -> dict[str, object]:
        """Return a JSON-serializable representation of this finding.

        Returns:
            A JSON-serializable dictionary representing this finding.
        """
        return asdict(self)


@dataclass
class PromptExtractionResult:
    """Structured report of prompt findings for a target repository."""

    target: str
    prompts: list[PromptFinding]

    @property
    def is_compliant(self) -> bool:
        """Extraction is informational; always returns True."""
        # Extraction is informational; always compliant.
        return True

    def to_json(self) -> dict[str, object]:
        """Return a JSON-serializable representation of this report.

        Returns:
            A JSON-serializable dictionary representing this report.
        """
        return {
            "target": self.target,
            "prompts": [p.to_json() for p in self.prompts],
            "is_compliant": self.is_compliant,
        }


def _looks_like_prompt_var(name: str) -> bool:
    lowered = name.lower()
    return any(lowered.endswith(suffix) for suffix in PROMPT_VAR_PATTERN)


def _extract_string(node: ast.expr) -> str | None:
    """Try to reduce an expression to a single string.

    Handles:
    - Constant strings
    - Concatenated strings via +
    - f-strings (expressions replaced with {...})

    Args:
        node: AST expression to reduce.

    Returns:
        String if the expression can be reduced; otherwise None.
    """
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value

    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        left = _extract_string(node.left)
        right = _extract_string(node.right)
        if left is not None and right is not None:
            return left + right

    if isinstance(node, ast.JoinedStr):
        parts: list[str] = []
        for value in node.values:
            if isinstance(value, ast.Constant) and isinstance(value.value, str):
                parts.append(value.value)
            else:
                parts.append("{...}")
        return "".join(parts)

    return None


def _prompts_from_assign(node: ast.Assign) -> list[tuple[str, int, str]]:
    results: list[tuple[str, int, str]] = []
    for target in node.targets:
        if isinstance(target, ast.Name) and _looks_like_prompt_var(target.id):
            value = _extract_string(node.value)
            if value:
                lineno = getattr(node, "lineno", 0)
                results.append((target.id, lineno, value))
    return results


def _prompts_from_annassign(node: ast.AnnAssign) -> list[tuple[str, int, str]]:
    if not (isinstance(node.target, ast.Name) and node.value):
        return []
    if not _looks_like_prompt_var(node.target.id):
        return []
    value = _extract_string(node.value)
    if not value:
        return []
    lineno = getattr(node, "lineno", 0)
    return [(node.target.id, lineno, value)]


def _extract_prompts_from_source(source: str) -> list[tuple[str, int, str]]:
    prompts: list[tuple[str, int, str]] = []
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


def _iter_code_files(root: Path, extensions: Iterable[str]) -> Iterable[Path]:
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix not in extensions:
            continue
        if any(part in IGNORE_DIRS for part in path.parts):
            continue
        yield path


def extract_prompts(
    target_root: Path,
    extensions: Sequence[str] = (".py",),
    min_length: int = 40,
) -> PromptExtractionResult:
    """Extract likely prompt variables from code under *target_root*.

    Args:
        target_root: Target repository root.
        extensions: File extensions to scan.
        min_length: Minimum length for extracted prompt strings.

    Returns:
        PromptExtractionResult containing extracted prompt findings.
    """
    findings: list[PromptFinding] = []
    for file_path in _iter_code_files(target_root, extensions):
        try:
            source = file_path.read_text(encoding="utf-8")
        except OSError:
            continue
        for var_name, lineno, value in _extract_prompts_from_source(source):
            if len(value.strip()) < min_length:
                continue
            findings.append(
                PromptFinding(
                    path=str(file_path.relative_to(target_root)),
                    line=lineno,
                    var_name=var_name,
                    value=value,
                )
            )
    return PromptExtractionResult(target=str(target_root), prompts=findings)


def print_human(result: PromptExtractionResult) -> None:
    """Print a human-readable prompt extraction summary.

    Args:
        result: Prompt extraction result to render.
    """
    print(f"Extracting prompts from: {result.target}\n")
    if not result.prompts:
        print("No inline prompts found.")
        return

    print(f"Found {len(result.prompts)} prompt(s):")
    for finding in result.prompts:
        preview = finding.value.strip().replace("\n", " ")
        if len(preview) > 80:
            preview = preview[:77] + "..."
        print(f"- {finding.path}:{finding.line} :: {finding.var_name} -> {preview}")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse CLI arguments for prompt extraction.

    Args:
        argv: Optional argv list.

    Returns:
        Parsed CLI arguments.
    """
    parser = argparse.ArgumentParser(
        prog="prompt_extract", description="Extract inline prompts into a report."
    )
    parser.add_argument(
        "--target-root", type=Path, default=Path("."), help="Path to target repo root"
    )
    parser.add_argument(
        "--json", action="store_true", help="Emit JSON instead of human-readable output"
    )
    parser.add_argument("--yaml", action="store_true", help="Emit prompts.yaml skeleton to stdout")
    parser.add_argument("--report", type=Path, help="Where to write the extraction report (JSON)")
    parser.add_argument(
        "--min-length", type=int, default=40, help="Minimum prompt length to include"
    )
    parser.add_argument(
        "--extensions",
        type=str,
        default=".py",
        help="Comma-separated list of file extensions to scan (e.g. .py,.pyi)",
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
    exts = tuple(ext.strip() for ext in args.extensions.split(",") if ext.strip())

    result = extract_prompts(
        target_root=target_root,
        extensions=exts,
        min_length=args.min_length,
    )
    payload = json.dumps(result.to_json(), indent=2)

    if args.yaml:
        yaml_lines = ["prompts:"]
        for idx, finding in enumerate(result.prompts, start=1):
            key = f"prompt_{idx}"
            yaml_lines.append(f"  {key}:")
            yaml_lines.append("    description: TODO")
            yaml_lines.append("    system: |")
            for line in finding.value.splitlines() or [""]:
                yaml_lines.append(f"      {line}")
            yaml_lines.append("    user_template: TODO")
            yaml_lines.append(f"    _source: {finding.path}:{finding.line} ({finding.var_name})")
        print("\n".join(yaml_lines))
    elif args.json:
        print(payload)
    else:
        print_human(result)

    if args.report:
        args.report.write_text(payload + "\n", encoding="utf-8")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
