#!/usr/bin/env python3
"""Coordinate audit remediation tasks described in docs/FIX_AUDIT_FINDINGS.md.

This tool enumerates known audit tasks, runs the ones that exist locally,
skips missing tools with a warning, and summarizes results. It is designed to
be resilient while some audit scripts are still TODO.
"""

from __future__ import annotations

import argparse
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Sequence


@dataclass(frozen=True)
class AuditTask:
    key: str
    title: str
    description: str
    command: List[str] | None
    path: Path | None


@dataclass
class TaskResult:
    task: AuditTask
    status: str  # ok | fail | missing | skipped
    exit_code: int | None
    stdout: str
    stderr: str

    @property
    def is_success(self) -> bool:
        return self.status == "ok"

    @property
    def is_missing(self) -> bool:
        return self.status == "missing"

    @property
    def is_failure(self) -> bool:
        return self.status == "fail"


KNOWN_TASKS: tuple[AuditTask, ...] = (
    AuditTask(
        key="structure",
        title="Structure Audit",
        description="Run audit_ai_project.py to check required files/folders.",
        command=["python", "scripts/audit_ai_project.py"],
        path=Path("scripts/audit_ai_project.py"),
    ),
    AuditTask(
        key="schema",
        title="Config & Schema Validation",
        description="Run ajv-validate.mjs to validate models/prompts YAML.",
        command=["node", "scripts/ajv-validate.mjs"],
        path=Path("scripts/ajv-validate.mjs"),
    ),
    AuditTask(
        key="prompt-extract",
        title="Prompt Extraction",
        description="(Placeholder) Move inline prompts into config/prompts.yaml.",
        command=None,
        path=None,
    ),
    AuditTask(
        key="prompt-merge",
        title="Prompt Merging",
        description="(Placeholder) Merge core/template/custom prompts.",
        command=None,
        path=Path("scripts/prompt_merge.py"),
    ),
    AuditTask(
        key="llm-usage",
        title="LLM Usage Audit",
        description="(Placeholder) Replace raw provider calls with standard clients.",
        command=["python", "scripts/audit_llm_usage.py"],
        path=Path("scripts/audit_llm_usage.py"),
    ),
    AuditTask(
        key="data-layout",
        title="Data Layout & Traceability",
        description="(Placeholder) Enforce data/ layout and metadata.",
        command=["python", "scripts/audit_data_layout.py"],
        path=Path("scripts/audit_data_layout.py"),
    ),
    AuditTask(
        key="tooling",
        title="Tooling & CI",
        description="(Placeholder) Align pre-commit and CI.",
        command=None,
        path=Path("scripts/audit_tooling.py"),
    ),
    AuditTask(
        key="docs",
        title="Docs & Standards",
        description="(Placeholder) Align README/docs with standards.",
        command=["python", "scripts/audit_docs.py"],
        path=Path("scripts/audit_docs.py"),
    ),
    AuditTask(
        key="health",
        title="Master Health Check",
        description="(Placeholder) Consolidated health check (rz_ai_check.py).",
        command=None,
        path=Path("scripts/rz_ai_check.py"),
    ),
)


WORKFLOW_GUIDE = """
Use the audits to see gaps, then fix with Copilot, then re-run audits.

Loop: run audit → inspect findings → open files → give Copilot explicit instructions → re-run audit.

1) Workspace: open both the standards repo and the target repo in a VS Code multi-root workspace so Copilot can reference standards.

2) Run audits from the target repo root (adjust paths to your standards repo):
   - python ../RZ-AI-Core-Standards/scripts/audit_ai_project.py
   - node ../RZ-AI-Core-Standards/scripts/ajv-validate.mjs
   - (future) audit_data_layout.py, audit_llm_usage.py, audit_tooling.py, audit_docs.py, rz_ai_check.py

3) Structure fixes: use Copilot with PROJECT_STRUCTURE.md and templates/data_layout.txt to create missing dirs/files and minimal config/models.yaml and config/prompts.yaml.

4) Prompts: move inline prompts into config/prompts.yaml; then rewire code to load prompts by id instead of hard-coded strings.

5) LLM usage: replace direct provider calls with standard clients (one per provider) that load prompts/models from config.

6) Data layout: write outputs under data/outputs with metadata (run_id, model, prompt_id, timestamp) and standard naming.

7) Tooling/CI: adapt pre-commit, ruff/mypy/pytest, and CI to the project; keep scope to languages actually used.

8) Docs: align README and local docs (AI_PROMPTING_STANDARDS, COPILOT_USAGE, PROJECT_STRUCTURE) with standards, keeping content project-specific.

9) Master check: once a consolidated checker exists, run it, fix one failing category at a time, and iterate until green.
"""

def resolve_tasks(standards_root: Path) -> list[AuditTask]:
    """Return tasks with commands rooted to the standards repo, preserving placeholders."""
    resolved: list[AuditTask] = []
    for task in KNOWN_TASKS:
        cmd = None
        if task.command:
            cmd = [
                str(standards_root / part) if part.startswith("scripts/") else part
                for part in task.command
            ]
        path = task.path
        if path is not None:
            path = standards_root / path
        resolved.append(
            AuditTask(
                key=task.key,
                title=task.title,
                description=task.description,
                command=cmd,
                path=path,
            )
        )
    return resolved


def run_task(task: AuditTask, *, cwd: Path, dry_run: bool = False) -> TaskResult:
    if task.command is None or (task.path is not None and not task.path.exists()):
        return TaskResult(task=task, status="missing", exit_code=None, stdout="", stderr="")

    if dry_run:
        return TaskResult(task=task, status="skipped", exit_code=0, stdout="DRY-RUN", stderr="")

    proc = subprocess.run(task.command, capture_output=True, text=True, cwd=cwd)
    status = "ok" if proc.returncode == 0 else "fail"
    return TaskResult(task=task, status=status, exit_code=proc.returncode, stdout=proc.stdout, stderr=proc.stderr)


def filter_tasks(tasks: Iterable[AuditTask], only: Sequence[str] | None) -> list[AuditTask]:
    if not only:
        return list(tasks)
    only_set = set(only)
    return [task for task in tasks if task.key in only_set]


def summarize(results: list[TaskResult]) -> str:
    lines = ["Task Key | Status | Exit | Notes", "--------|--------|------|------"]
    for result in results:
        note = ""
        if result.is_missing:
            note = "missing script"
        elif result.status == "skipped":
            note = "dry-run"
        elif result.is_failure:
            note = (result.stderr or result.stdout).strip().splitlines()[0] if (result.stderr or result.stdout) else "failed"
        lines.append(f"{result.task.key} | {result.status} | {result.exit_code if result.exit_code is not None else '-'} | {note}")
    return "\n".join(lines)


def write_plan(path: Path, results: list[TaskResult]) -> None:
    lines: list[str] = ["# Audit Remediation Plan", ""]
    for res in results:
        lines.append(f"## {res.task.title} ({res.task.key})")
        lines.append(f"Status: {res.status}")
        if res.exit_code is not None:
            lines.append(f"Exit code: {res.exit_code}")
        if res.stdout.strip():
            lines.append("### Output")
            lines.append("```\n" + res.stdout.strip() + "\n```")
        if res.stderr.strip():
            lines.append("### Errors")
            lines.append("```\n" + res.stderr.strip() + "\n```")
        if res.is_missing:
            lines.append("_Script missing; see FIX_AUDIT_FINDINGS.md for guidance._")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def run_sequence(
    tasks: list[AuditTask],
    *,
    target_root: Path,
    dry_run: bool,
) -> list[TaskResult]:
    return [run_task(task, cwd=target_root, dry_run=dry_run) for task in tasks]


def main(argv: Sequence[str] | None = None) -> int:  # noqa: C901
    parser = argparse.ArgumentParser(description="Run or list AI Core Standards audit remediation tasks.")
    parser.add_argument("--list", action="store_true", help="List tasks and exit")
    parser.add_argument("--run", action="store_true", help="Run tasks (default: list only)")
    parser.add_argument("--only", help="Comma-separated task keys to run (e.g., structure,schema)")
    parser.add_argument("--dry-run", action="store_true", help="Do not execute commands; show what would run")
    parser.add_argument("--fail-on-missing", action="store_true", help="Return non-zero if any requested task is missing")
    parser.add_argument("--guide", action="store_true", help="Print remediation workflow guidance and exit")
    parser.add_argument("--standards-root", type=Path, help="Path to the standards repo containing audit scripts")
    parser.add_argument("--target-root", type=Path, help="Path to the target project to audit (defaults to current repo)")
    parser.add_argument("--plan-path", type=Path, help="Where to write the remediation plan (default: target_root/fix_audit_plan.md)")
    parser.add_argument("--loop", action="store_true", help="Re-run audits up to max iterations until success")
    parser.add_argument("--max-iterations", type=int, default=3, help="Max iterations when --loop is set (default: 3)")
    parser.add_argument("--skip-plan", action="store_true", help="Do not write remediation plan file")
    args = parser.parse_args(argv)

    repo_root = Path(__file__).resolve().parents[1]
    standards_root = args.standards_root.resolve() if args.standards_root else repo_root
    target_root = args.target_root.resolve() if args.target_root else repo_root

    tasks = resolve_tasks(standards_root)
    only_keys = args.only.split(",") if args.only else None
    selected = filter_tasks(tasks, only_keys)

    if args.guide:
        print(WORKFLOW_GUIDE)
        return 0

    if args.list and not args.run:
        for task in selected:
            availability = "missing" if (task.command is None or (task.path and not task.path.exists())) else "available"
            print(f"{task.key:15s} {availability:10s} - {task.title}")
        return 0

    if not args.run:
        parser.print_help()
        return 0

    plan_path = args.plan_path if args.plan_path else (target_root / "fix_audit_plan.md")

    def run_once() -> list[TaskResult]:
        return run_sequence(selected, target_root=target_root, dry_run=args.dry_run)

    iterations = args.max_iterations if args.loop else 1
    results: list[TaskResult] = []
    for _ in range(iterations):
        results = run_once()
        print(summarize(results))
        if not args.skip_plan:
            write_plan(plan_path, results)

        failures = [r for r in results if r.is_failure]
        missing = [r for r in results if r.is_missing]

        if not failures and (not args.fail_on_missing or not missing):
            break

    failures = [r for r in results if r.is_failure]
    missing = [r for r in results if r.is_missing]

    if failures:
        return 1
    if args.fail_on_missing and missing:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
