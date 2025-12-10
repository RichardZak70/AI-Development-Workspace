"""Tests for fix_audit_findings orchestrator."""

# pyright: reportMissingImports=false, reportUnknownVariableType=false, reportUnknownMemberType=false

import sys
from pathlib import Path
from typing import Any, cast


# Ensure scripts/ is importable
ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from fix_audit_findings import AuditTask, run_task, summarize  # noqa: E402

AuditTask = cast(Any, AuditTask)
run_task = cast(Any, run_task)
summarize = cast(Any, summarize)


def test_run_task_marks_missing_when_command_absent() -> None:
    task: Any = AuditTask(
        key="missing",
        title="Missing Task",
        description="No command",
        command=None,
        path=None,
    )

    result: Any = run_task(task, cwd=ROOT)

    assert result.status == "missing"
    assert result.exit_code is None


def test_run_task_executes_available(tmp_path: Path) -> None:
    script = tmp_path / "dummy.py"
    script.write_text("print('hello')", encoding="utf-8")

    task: Any = AuditTask(
        key="dummy",
        title="Dummy",
        description="",
        command=[sys.executable, str(script)],
        path=script,
    )

    result: Any = run_task(task, cwd=tmp_path)

    assert result.status == "ok"
    assert result.exit_code == 0
    assert "hello" in result.stdout


def test_summarize_formats_output() -> None:
    missing: Any = run_task(
        AuditTask(
            key="missing",
            title="Missing",
            description="",
            command=None,
            path=None,
        ),
        cwd=ROOT,
    )

    text = summarize([missing])

    assert "missing" in text
    assert "Task Key" in text


def test_guide_flag_prints_workflow(capsys: Any) -> None:
    # Invoke main in-process to ensure the guide renders without error.
    from fix_audit_findings import main

    exit_code = main(["--guide"])

    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Use the audits" in captured.out
