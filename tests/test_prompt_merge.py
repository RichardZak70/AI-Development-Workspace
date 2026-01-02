"""Tests for prompt merging utilities and CLI."""

import importlib
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

mod = importlib.import_module("prompt_merge")
merge_prompts = getattr(mod, "merge_prompts")
write_yaml = getattr(mod, "write_yaml")
_load_yaml = getattr(mod, "_load_yaml")
main = getattr(mod, "main")


def _write_yaml(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


# ---------------------------------------------------------------------------
# Unit-level tests for merge_prompts (no filesystem)
# ---------------------------------------------------------------------------


def test_merge_prompts_reports_overrides_and_sources() -> None:
    """merge_prompts records merged values, sources, and overrides."""
    core = {"a": "core", "shared": "core"}
    template = {"b": "template", "shared": "template"}
    project = {"c": "project", "shared": "project"}

    report = merge_prompts(core, template, project)

    assert report.merged == {
        "a": "core",
        "b": "template",
        "c": "project",
        "shared": "project",
    }

    assert report.source_by_key == {
        "a": "core",
        "b": "template",
        "c": "project",
        "shared": "project",
    }

    assert report.overrides["shared"] == ["core", "template", "project"]


# ---------------------------------------------------------------------------
# CLI-level tests (main, _load_yaml, write_yaml)
# ---------------------------------------------------------------------------


def test_merge_precedence_and_overrides(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """CLI merges prompts with precedence and reports overrides."""
    core = tmp_path / "core.yaml"
    template = tmp_path / "template.yaml"
    project = tmp_path / "project.yaml"
    output = tmp_path / "out.yaml"

    _write_yaml(
        core,
        """a: core
shared: core
""",
    )
    _write_yaml(
        template,
        """b: template
shared: template
""",
    )
    _write_yaml(
        project,
        """c: project
shared: project
""",
    )

    exit_code = main(
        [
            "--core",
            str(core),
            "--template",
            str(template),
            "--project",
            str(project),
            "--output",
            str(output),
            "--show-overrides",
        ]
    )

    assert exit_code == 0
    merged = _load_yaml(output)
    assert merged["shared"] == "project"
    assert merged["a"] == "core"
    assert merged["b"] == "template"
    assert merged["c"] == "project"

    err = capsys.readouterr().err
    assert "Overrides detected" in err
    assert "shared" in err
    assert "core" in err
    assert "template" in err


def test_missing_file_errors(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """CLI returns non-zero when required core file is missing."""
    missing = tmp_path / "missing.yaml"
    result = main(["--core", str(missing)])

    assert result == 1
    err = capsys.readouterr().err
    assert "Missing required prompts file" in err


def test_write_yaml_creates_parent(tmp_path: Path) -> None:
    """write_yaml creates parent directories as needed."""
    data = {"x": 1}
    target = tmp_path / "nested" / "file.yaml"

    write_yaml(data, target)

    assert target.exists()
    loaded = _load_yaml(target)
    assert loaded == data


def test_load_yaml_rejects_non_mapping(tmp_path: Path) -> None:
    """_load_yaml rejects YAML documents that are not mappings."""
    bad = tmp_path / "bad.yaml"
    _write_yaml(bad, "- not a mapping")

    with pytest.raises(ValueError):
        _load_yaml(bad)


def test_optional_template_and_project_are_skipped(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Optional template/project files are skipped when missing."""
    core = tmp_path / "core.yaml"
    _write_yaml(core, "core_prompt: core")
    output = tmp_path / "merged.yaml"

    exit_code = main(
        [
            "--core",
            str(core),
            "--template",
            str(tmp_path / "missing_template.yaml"),
            "--project",
            str(tmp_path / "missing_project.yaml"),
            "--output",
            str(output),
        ]
    )

    assert exit_code == 0
    merged = _load_yaml(output)
    assert merged == {"core_prompt": "core"}
    err = capsys.readouterr().err
    assert "Optional prompts file not found" in err


def test_dry_run_does_not_write(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """--dry-run does not write the output file."""
    core = tmp_path / "core.yaml"
    _write_yaml(core, "core_prompt: core")
    output = tmp_path / "out.yaml"

    exit_code = main(
        [
            "--core",
            str(core),
            "--output",
            str(output),
            "--dry-run",
        ]
    )

    assert exit_code == 0
    assert not output.exists()
    out = capsys.readouterr().out
    assert "[dry-run]" in out


def test_show_overrides_silent_when_no_overrides(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """If there are no overlapping keys, --show-overrides should not print an overrides block."""
    core = tmp_path / "core.yaml"
    template = tmp_path / "template.yaml"
    project = tmp_path / "project.yaml"
    output = tmp_path / "out.yaml"

    _write_yaml(core, "core_only: 1\n")
    _write_yaml(template, "template_only: 2\n")
    _write_yaml(project, "project_only: 3\n")

    exit_code = main(
        [
            "--core",
            str(core),
            "--template",
            str(template),
            "--project",
            str(project),
            "--output",
            str(output),
            "--show-overrides",
        ]
    )

    assert exit_code == 0
    err = capsys.readouterr().err
    assert "Overrides detected" not in err
