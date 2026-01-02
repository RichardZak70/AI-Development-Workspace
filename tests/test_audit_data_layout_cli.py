"""CLI-related tests for the data layout audit."""

import importlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

mod = importlib.import_module("audit_data_layout")
audit = getattr(mod, "audit")


def _make_dirs(base: Path, dirs: list[str]) -> None:
    for rel in dirs:
        (base / rel).mkdir(parents=True, exist_ok=True)


def test_custom_metadata_schema_is_used(tmp_path: Path) -> None:
    """Custom metadata schema is used when provided to the audit."""
    # create required dirs
    required_dirs = getattr(mod, "REQUIRED_DIRS")
    _make_dirs(tmp_path, required_dirs)
    outputs_dir = tmp_path / "data" / "outputs"

    # write output missing "run_id" (will fail when schema requires it)
    bad = outputs_dir / "out.json"
    bad.write_text(json.dumps({"prompt_id": "p1"}), encoding="utf-8")

    # custom schema requiring run_id
    schema_path = tmp_path / "schema.json"
    schema_path.write_text(
        json.dumps(
            {
                "$schema": "https://json-schema.org/draft/2020-12/schema",
                "type": "object",
                "required": ["run_id"],
                "properties": {"run_id": {"type": "string"}},
            }
        ),
        encoding="utf-8",
    )

    result = audit(tmp_path, metadata_schema=schema_path)

    assert result.is_compliant is False
    assert any("run_id" in issue for issue in result.metadata_issues)
