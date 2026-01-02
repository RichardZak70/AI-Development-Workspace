"""Tests for documentation presence/linkage audit."""

import importlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

docs_mod = importlib.import_module("audit_docs")
REQUIRED_DOCS = getattr(docs_mod, "REQUIRED_DOCS")
RECOMMENDED_DOCS = getattr(docs_mod, "RECOMMENDED_DOCS")
audit = getattr(docs_mod, "audit")


def _touch_files(base: Path, rels: list[str]) -> None:
    for rel in rels:
        path = base / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch()


def test_compliant_when_all_docs_and_readme_links(tmp_path: Path) -> None:
    """All required + recommended docs exist and are referenced in README."""
    _touch_files(tmp_path, REQUIRED_DOCS + RECOMMENDED_DOCS)
    links = "\n".join(f"- see {rel}" for rel in REQUIRED_DOCS)
    (tmp_path / "README.md").write_text(links, encoding="utf-8")

    result = audit(tmp_path)

    assert result.is_compliant is True
    assert result.missing_required == []
    assert result.missing_recommended == []
    assert result.readme_missing is False
    assert result.unlinked_required == []


def test_missing_required_docs_fails(tmp_path: Path) -> None:
    """If required docs are missing, project is not compliant."""
    (tmp_path / "README.md").write_text("README", encoding="utf-8")

    result = audit(tmp_path)

    assert result.is_compliant is False
    assert set(result.missing_required) == set(REQUIRED_DOCS)
    assert result.unlinked_required == []
    assert set(result.missing_recommended) == set(RECOMMENDED_DOCS)


def test_missing_readme_marks_non_compliant(tmp_path: Path) -> None:
    """If README is missing, project is not compliant but unlinked list stays empty."""
    _touch_files(tmp_path, REQUIRED_DOCS)

    result = audit(tmp_path)

    assert result.readme_missing is True
    assert result.is_compliant is False
    assert result.unlinked_required == []
    assert set(result.missing_recommended) == set(RECOMMENDED_DOCS)


def test_unlinked_required_docs_fail(tmp_path: Path) -> None:
    """Required docs exist but are not referenced in README -> non-compliant."""
    _touch_files(tmp_path, REQUIRED_DOCS)
    (tmp_path / "README.md").write_text("no links here", encoding="utf-8")

    result = audit(tmp_path)

    assert result.is_compliant is False
    assert set(result.unlinked_required) == set(REQUIRED_DOCS)
    assert set(result.missing_recommended) == set(RECOMMENDED_DOCS)


def test_recommended_missing_only_warns(tmp_path: Path) -> None:
    """Recommended docs missing should not break compliance.

    If all required docs exist and are linked, but recommended docs are missing,
    the project should still be compliant.
    """
    _touch_files(tmp_path, REQUIRED_DOCS)
    links = "\n".join(f"- see {rel}" for rel in REQUIRED_DOCS)
    (tmp_path / "README.md").write_text(links, encoding="utf-8")

    result = audit(tmp_path)

    assert result.missing_required == []
    assert result.readme_missing is False
    assert result.unlinked_required == []
    assert set(result.missing_recommended) == set(RECOMMENDED_DOCS)
    assert result.is_compliant is True


def test_json_report_serialization(tmp_path: Path) -> None:
    """to_json() returns a structure that can be round-tripped through JSON."""
    _touch_files(tmp_path, REQUIRED_DOCS)
    (tmp_path / "README.md").write_text("see nothing", encoding="utf-8")

    result = audit(tmp_path)
    payload = result.to_json()
    serialized = json.loads(json.dumps(payload))

    assert "missing_required" in serialized
    assert "missing_recommended" in serialized
    assert "readme_missing" in serialized
    assert "unlinked_required" in serialized
    assert "is_compliant" in serialized
