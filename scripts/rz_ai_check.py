#!/usr/bin/env python3
"""Run consolidated health checks for AI-Core-Standards repositories."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, List

from audit_data_layout import audit as audit_data_layout
from audit_tooling import audit as audit_tooling
from prompt_extract import extract_prompts


@dataclass
class CheckResult:
    """Outcome of a single named check in the consolidated report."""

    name: str
    status: str  # "pass" | "fail"
    details: dict[str, Any]

    def to_json(self) -> dict[str, Any]:
        """Return a JSON-serializable representation of this check.

        Returns:
            A JSON-serializable dictionary representing this check.
        """
        return asdict(self)


@dataclass
class ConsolidatedReport:
    """Aggregate report across multiple audits/checks for one target."""

    target: str
    checks: List[CheckResult]

    @property
    def passed(self) -> bool:
        """Return True if all checks passed."""
        return all(check.status == "pass" for check in self.checks)

    def to_json(self) -> dict[str, Any]:
        """Return a JSON-serializable representation of this report.

        Returns:
            A JSON-serializable dictionary representing this report.
        """
        return {
            "target": self.target,
            "passed": self.passed,
            "checks": [c.to_json() for c in self.checks],
        }


def run_checks(target_root: Path) -> ConsolidatedReport:
    """Run the consolidated checks against *target_root*.

    Args:
        target_root: Target repository root.

    Returns:
        ConsolidatedReport containing check results.
    """
    checks: list[CheckResult] = []

    tooling_result = audit_tooling(target_root)
    checks.append(
        CheckResult(
            name="tooling",
            status="pass" if tooling_result.is_compliant else "fail",
            details=tooling_result.to_json(),
        )
    )

    data_result = audit_data_layout(target_root)
    checks.append(
        CheckResult(
            name="data_layout",
            status="pass" if data_result.is_compliant else "fail",
            details=data_result.to_json(),
        )
    )

    prompt_result = extract_prompts(target_root)
    checks.append(
        CheckResult(
            name="prompt_extract",
            status="pass",  # informational only
            details={
                "prompt_count": len(prompt_result.prompts),
                "target": prompt_result.target,
            },
        )
    )

    return ConsolidatedReport(target=str(target_root), checks=checks)


def print_human(report: ConsolidatedReport) -> None:
    """Print a human-readable consolidated report.

    Args:
        report: Consolidated report to render.
    """
    print(f"Running AI-Core consolidated checks for: {report.target}\n")
    for check in report.checks:
        mark = "✅" if check.status == "pass" else "❌"
        print(f"{mark} {check.name}")
    print()
    print("Overall:", "PASS" if report.passed else "FAIL")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse CLI arguments for the consolidated check runner.

    Args:
        argv: Optional argv list.

    Returns:
        Parsed CLI arguments.
    """
    parser = argparse.ArgumentParser(
        prog="rz_ai_check",
        description="Run consolidated AI-Core-Standards health check.",
    )
    parser.add_argument(
        "--target-root", type=Path, default=Path("."), help="Path to target repo root"
    )
    parser.add_argument(
        "--json", action="store_true", help="Emit JSON instead of human-readable output"
    )
    parser.add_argument("--report", type=Path, help="Where to write the consolidated report (JSON)")
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

    report = run_checks(target_root)
    payload = json.dumps(report.to_json(), indent=2)

    if args.json:
        print(payload)
    else:
        print_human(report)

    if args.report:
        args.report.write_text(payload + "\n", encoding="utf-8")

    return 0 if report.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
