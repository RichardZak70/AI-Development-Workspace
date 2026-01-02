"""Tests for the consolidated AI standards check runner."""

import importlib
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

mod = importlib.import_module("rz_ai_check")
run_checks = getattr(mod, "run_checks")
main = getattr(mod, "main")


def _touch(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("", encoding="utf-8")


def _setup_compliant_repo(root: Path) -> None:
    # Tooling minimal compliance
    _touch(root / ".pre-commit-config.yaml")
    _touch(root / "pyproject.toml")
    _touch(root / ".github" / "workflows" / "ci.yml")

    # Data layout required dirs
    for rel in [
        "data",
        "data/raw",
        "data/processed",
        "data/prompts",
        "data/outputs",
        "data/cache",
        "data/embeddings",
    ]:
        (root / rel).mkdir(parents=True, exist_ok=True)

    # Prompt example
    (root / "service").mkdir(parents=True, exist_ok=True)
    long_prompt = "You are a helpful assistant who answers succinctly."  # > min_length default
    (root / "service" / "prompts.py").write_text(
        f"SYSTEM_PROMPT = '{long_prompt}'", encoding="utf-8"
    )


def test_run_checks_passes_when_all_compliant(tmp_path: Path) -> None:
    """run_checks passes when the target repo meets all requirements."""
    _setup_compliant_repo(tmp_path)

    report = run_checks(tmp_path)

    assert report.passed is True
    names = {c.name for c in report.checks}
    assert {"tooling", "data_layout", "prompt_extract"} <= names
    # prompt_extract details include count
    prompt_check = next(c for c in report.checks if c.name == "prompt_extract")
    assert prompt_check.details["prompt_count"] == 1


def test_main_json_output_and_exit_code(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Main emits JSON and returns 0 on success."""
    _setup_compliant_repo(tmp_path)

    exit_code = main(["--target-root", str(tmp_path), "--json"])

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["passed"] is True
    assert len(payload["checks"]) == 3


def test_main_fails_when_data_layout_missing(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Main returns non-zero when a required check fails."""
    # Only create tooling compliance; skip data dirs
    _touch(tmp_path / ".pre-commit-config.yaml")
    _touch(tmp_path / "pyproject.toml")
    _touch(tmp_path / ".github" / "workflows" / "ci.yml")

    exit_code = main(["--target-root", str(tmp_path), "--json"])

    assert exit_code == 1
    out = capsys.readouterr().out
    payload = json.loads(out)
    assert payload["passed"] is False
    statuses = {c["name"]: c["status"] for c in payload["checks"]}
    assert statuses["data_layout"] == "fail"
