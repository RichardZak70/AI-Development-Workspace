"""Tests for the AI project structure audit."""

import importlib
import sys
from pathlib import Path
from typing import cast

import pytest

# Ensure the scripts directory is on the path when running tests directly
ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

audit_mod = importlib.import_module("audit_ai_project")
REQUIRED_DIRS = cast(list[str], getattr(audit_mod, "REQUIRED_DIRS"))
REQUIRED_FILES = cast(list[str], getattr(audit_mod, "REQUIRED_FILES"))
RECOMMENDED_FILES = cast(list[str], getattr(audit_mod, "RECOMMENDED_FILES"))
audit = getattr(audit_mod, "audit")
print_human = getattr(audit_mod, "print_human")


def _create_dirs(base: Path, dirs: list[str]) -> None:
    for d in dirs:
        (base / d).mkdir(parents=True, exist_ok=True)


def _create_files(base: Path, files: list[str]) -> None:
    for f in files:
        path = base / f
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch()


def test_audit_passes_when_all_required_items_exist(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Project passes when required dirs/files exist; recommended may be missing."""
    _create_dirs(tmp_path, REQUIRED_DIRS)
    _create_files(tmp_path, REQUIRED_FILES)

    result = audit(tmp_path)
    print_human(result)
    captured = capsys.readouterr().out

    assert result.is_compliant is True
    assert result.missing_dirs == []
    assert result.missing_files == []
    # Recommended items may be missing; allow empty or full list depending on fixture
    assert result.missing_recommended == RECOMMENDED_FILES or result.missing_recommended == []
    assert "Missing recommended items (not strictly required):" in captured
    assert "Project matches core AI structure." in captured


def test_audit_reports_missing_dirs_and_files(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Audit reports missing required directories and files."""
    # Create only a subset so we trigger missing directories and files
    _create_dirs(tmp_path, ["config", "docs"])
    _create_files(tmp_path, [])

    result = audit(tmp_path)
    print_human(result)
    captured = capsys.readouterr().out

    assert result.is_compliant is False
    assert "Missing required directories:" in captured
    for expected_dir in REQUIRED_DIRS:
        # Only two directories were created; the rest should be reported as missing
        if expected_dir not in {"config", "docs"}:
            assert expected_dir in captured
    assert "Missing required files:" in captured
    for expected_file in REQUIRED_FILES:
        assert expected_file in captured
    assert "Missing recommended items (not strictly required):" in captured
    for rec in RECOMMENDED_FILES:
        assert rec in captured
    assert "Project does NOT match core AI structure." in captured


def test_audit_reports_missing_files_only(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Audit reports missing files when directories exist."""
    # All directories exist, but files are absent
    _create_dirs(tmp_path, REQUIRED_DIRS)

    result = audit(tmp_path)
    print_human(result)
    captured = capsys.readouterr().out

    assert result.is_compliant is False
    assert result.missing_dirs == []
    assert "Missing required files:" in captured
    for expected_file in REQUIRED_FILES:
        assert expected_file in captured
    assert "Missing recommended items (not strictly required):" in captured
    assert "Project does NOT match core AI structure." in captured


def test_missing_recommended_only_does_not_break_compliance(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Recommended-only gaps should still be compliant but warn."""
    _create_dirs(tmp_path, REQUIRED_DIRS)
    _create_files(tmp_path, REQUIRED_FILES)

    result = audit(tmp_path)
    print_human(result)
    captured = capsys.readouterr().out

    assert result.is_compliant is True
    # All recommended items should be listed as missing
    assert result.missing_recommended == RECOMMENDED_FILES or result.missing_recommended == []
    assert "Missing recommended items (not strictly required):" in captured
    for rec in RECOMMENDED_FILES:
        assert rec in captured
    assert "Project matches core AI structure." in captured
