"""Tests for the data layout and traceability audit."""

import importlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

data_mod = importlib.import_module("audit_data_layout")
REQUIRED_DIRS = getattr(data_mod, "REQUIRED_DIRS")
audit = getattr(data_mod, "audit")


def _make_dirs(base: Path, dirs: list[str]) -> None:
    for rel in dirs:
        (base / rel).mkdir(parents=True, exist_ok=True)


def test_pass_when_required_dirs_and_metadata(tmp_path: Path) -> None:
    """Audit passes when required dirs exist and output metadata is valid."""
    _make_dirs(tmp_path, REQUIRED_DIRS)
    out_file = tmp_path / "data" / "outputs" / "result.json"
    out_file.write_text(
        """{
        "run_id": "r1",
        "model": "gpt-4",
        "prompt_id": "p1",
        "timestamp": "2024-01-01T00:00:00Z",
        "status": "success"
        }""",
        encoding="utf-8",
    )

    result = audit(tmp_path)

    assert result.is_compliant is True
    assert result.missing_dirs == []
    assert result.metadata_issues == []
    assert result.stray_items == []


def test_missing_dirs_flags_noncompliance(tmp_path: Path) -> None:
    """Audit fails when required directories are missing."""
    # Only create data/outputs to avoid having all required dirs
    (tmp_path / "data" / "outputs").mkdir(parents=True, exist_ok=True)

    result = audit(tmp_path)

    assert result.is_compliant is False
    assert "data/raw" in result.missing_dirs
    assert "data/processed" in result.missing_dirs


def test_missing_metadata_detected(tmp_path: Path) -> None:
    """Audit fails when output JSON is missing required metadata fields."""
    _make_dirs(tmp_path, REQUIRED_DIRS)
    out_file = tmp_path / "data" / "outputs" / "bad.json"
    out_file.write_text("{}", encoding="utf-8")

    result = audit(tmp_path)

    assert result.is_compliant is False
    assert result.metadata_issues
    assert any("schema validation failed" in issue for issue in result.metadata_issues)


def test_stray_items_under_data_are_reported(tmp_path: Path) -> None:
    """Audit reports stray files/directories under data/."""
    _make_dirs(tmp_path, REQUIRED_DIRS)
    extra_dir = tmp_path / "data" / "tmp"
    extra_dir.mkdir(parents=True, exist_ok=True)
    extra_file = tmp_path / "data" / "random.txt"
    extra_file.write_text("junk", encoding="utf-8")

    result = audit(tmp_path)

    assert result.is_compliant is False
    stray = {item.replace("\\", "/") for item in result.stray_items}
    assert "data/tmp" in stray
    assert "data/random.txt" in stray


def test_allowed_top_level_files_not_flagged(tmp_path: Path) -> None:
    """Allowed housekeeping files under data/ are not flagged as stray."""
    _make_dirs(tmp_path, REQUIRED_DIRS)
    (tmp_path / "data" / ".gitkeep").write_text("", encoding="utf-8")
    (tmp_path / "data" / ".gitignore").write_text("", encoding="utf-8")
    (tmp_path / "data" / "README.md").write_text("data layout", encoding="utf-8")

    result = audit(tmp_path)

    assert "data/.gitkeep" not in result.stray_items
    assert "data/.gitignore" not in result.stray_items
    assert "data/README.md" not in result.stray_items


def test_malformed_json_output_is_reported(tmp_path: Path) -> None:
    """Audit reports malformed JSON outputs."""
    _make_dirs(tmp_path, REQUIRED_DIRS)
    out_file = tmp_path / "data" / "outputs" / "broken.json"
    out_file.write_text("{not: valid json", encoding="utf-8")

    result = audit(tmp_path)

    assert result.is_compliant is False
    assert any("failed to parse JSON" in issue for issue in result.metadata_issues)


def test_non_object_json_output_is_reported(tmp_path: Path) -> None:
    """Audit reports outputs whose top-level JSON is not an object."""
    _make_dirs(tmp_path, REQUIRED_DIRS)
    out_file = tmp_path / "data" / "outputs" / "array.json"
    out_file.write_text('["a", "b", "c"]', encoding="utf-8")

    result = audit(tmp_path)

    assert result.is_compliant is False
    assert any("expected top-level JSON object" in issue for issue in result.metadata_issues)


def test_invalid_timestamp_fails_schema_validation(tmp_path: Path) -> None:
    """Audit fails schema validation when timestamp format is invalid."""
    _make_dirs(tmp_path, REQUIRED_DIRS)
    out_file = tmp_path / "data" / "outputs" / "bad_ts.json"
    out_file.write_text(
        """{
        "run_id": "r1",
        "model": "gpt-4",
        "prompt_id": "p1",
        "timestamp": "not-a-date"
        }""",
        encoding="utf-8",
    )

    result = audit(tmp_path)

    assert result.is_compliant is False
    assert any("schema validation failed" in issue for issue in result.metadata_issues)


def test_max_output_files_limits_scan(tmp_path: Path) -> None:
    """Audit truncates metadata checks when max_output_files is exceeded."""
    _make_dirs(tmp_path, REQUIRED_DIRS)
    outputs_dir = tmp_path / "data" / "outputs"
    for i in range(5):
        (outputs_dir / f"out_{i}.json").write_text("{}", encoding="utf-8")

    result = audit(tmp_path, max_output_files=2)

    assert result.is_compliant is False
    assert any("metadata check truncated" in issue for issue in result.metadata_issues)
