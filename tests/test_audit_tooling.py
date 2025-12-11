import importlib
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

mod = importlib.import_module("audit_tooling")
audit = getattr(mod, "audit")
print_human = getattr(mod, "print_human")
REQUIRED_FILES = getattr(mod, "REQUIRED_FILES")
RECOMMENDED_FILES = getattr(mod, "RECOMMENDED_FILES")
RECOMMENDED_DIRS = getattr(mod, "RECOMMENDED_DIRS")
CI_SENTINEL = getattr(mod, "CI_SENTINEL")


def _touch(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.touch()


def test_compliant_when_required_and_recommended_present(tmp_path: Path) -> None:
    """If all required + recommended files/dirs exist, project is fully compliant."""
    for rel in REQUIRED_FILES:
        _touch(tmp_path / rel)
    for rel in RECOMMENDED_FILES:
        _touch(tmp_path / rel)
    for rel in RECOMMENDED_DIRS:
        (tmp_path / rel).mkdir(parents=True, exist_ok=True)

    result = audit(tmp_path)

    assert result.is_compliant is True
    assert result.missing_required == []
    assert result.missing_recommended == []
    assert result.missing_recommended_dirs == []


def test_missing_required_fails_for_python_repo(tmp_path: Path) -> None:
    """
    Presence of Python code should trigger Python-specific requirements
    (.pre-commit-config.yaml, pyproject.toml, CI sentinel, etc).
    """
    _touch(tmp_path / "src" / "app.py")  # Python project

    result = audit(tmp_path)

    assert result.is_compliant is False
    assert ".pre-commit-config.yaml" in result.missing_required
    assert "pyproject.toml" in result.missing_required
    assert set(result.missing_recommended_dirs) == set(RECOMMENDED_DIRS)


def test_recommended_missing_warns_only_when_no_language(tmp_path: Path) -> None:
    """
    If there are no language-specific source files, recommended items are listed
    but do not break compliance when required core tooling is present.
    """
    for rel in REQUIRED_FILES:
        _touch(tmp_path / rel)

    result = audit(tmp_path)

    assert result.is_compliant is True
    assert set(result.missing_recommended) == set(RECOMMENDED_FILES)
    assert set(result.missing_recommended_dirs) == set(RECOMMENDED_DIRS)


def test_json_round_trip(tmp_path: Path) -> None:
    """Result.to_json() should round-trip cleanly through JSON."""
    for rel in REQUIRED_FILES:
        _touch(tmp_path / rel)
    for rel in RECOMMENDED_FILES:
        _touch(tmp_path / rel)
    for rel in RECOMMENDED_DIRS:
        (tmp_path / rel).mkdir(parents=True, exist_ok=True)

    result = audit(tmp_path)
    payload = result.to_json()
    serialized = json.loads(json.dumps(payload))

    assert "missing_required" in serialized
    assert "missing_recommended" in serialized
    assert "missing_recommended_dirs" in serialized
    assert "is_compliant" in serialized
    assert serialized["is_compliant"] is True


def test_human_output_includes_missing(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Human output should mention missing required tooling when nothing is present."""
    result = audit(tmp_path)

    print_human(result)
    out = capsys.readouterr().out

    assert "Missing required" in out or "Missing required tooling files" in out
    assert any(req in out for req in REQUIRED_FILES)


def test_ci_workflow_any_file_satisfies(tmp_path: Path) -> None:
    """
    Any workflow file under .github/workflows/ should satisfy the CI sentinel,
    even if its name is not exactly ci.yml.
    """
    _touch(tmp_path / ".pre-commit-config.yaml")
    _touch(tmp_path / "pyproject.toml")
    _touch(tmp_path / ".github" / "workflows" / "alt.yaml")

    result = audit(tmp_path)

    assert result.is_compliant is True
    assert any(r in result.missing_recommended for r in RECOMMENDED_FILES)
    assert "tests" in result.missing_recommended_dirs


def test_ruff_alternative_config(tmp_path: Path) -> None:
    """Either ruff.toml or .ruff.toml should satisfy 'ruff config' recommendation."""
    for rel in REQUIRED_FILES:
        _touch(tmp_path / rel)
    (tmp_path / "tests").mkdir(parents=True, exist_ok=True)
    _touch(tmp_path / ".ruff.toml")

    result = audit(tmp_path)

    assert result.is_compliant is True
    assert "ruff.toml" not in result.missing_recommended
    assert ".ruff.toml" not in result.missing_recommended


def test_js_requires_package_json(tmp_path: Path) -> None:
    """
    JS project: .js should require package.json, but not pyproject.toml when no Python.
    """
    _touch(tmp_path / "src" / "index.js")
    _touch(tmp_path / CI_SENTINEL)
    _touch(tmp_path / ".pre-commit-config.yaml")

    result = audit(tmp_path)

    assert "package.json" in result.missing_required
    assert "pyproject.toml" not in result.missing_required


def test_ts_requires_tsconfig_and_package_json(tmp_path: Path) -> None:
    """
    TS project: .ts should require both package.json and tsconfig.json.
    """
    _touch(tmp_path / "src" / "app.ts")
    _touch(tmp_path / CI_SENTINEL)
    _touch(tmp_path / ".pre-commit-config.yaml")

    result = audit(tmp_path)

    assert "package.json" in result.missing_required
    assert "tsconfig.json" in result.missing_required
    assert "pyproject.toml" not in result.missing_required


def test_c_cpp_requires_build_system(tmp_path: Path) -> None:
    """
    C/C++ project: .c should require a build system file (CMakeLists.txt or Makefile) but not pyproject.toml.
    """
    _touch(tmp_path / "src" / "main.c")
    _touch(tmp_path / CI_SENTINEL)
    _touch(tmp_path / ".pre-commit-config.yaml")

    result = audit(tmp_path)

    assert any(m in result.missing_required for m in {"CMakeLists.txt", "Makefile"})
    assert "pyproject.toml" not in result.missing_required


def test_mixed_python_and_js_requires_union(tmp_path: Path) -> None:
    """
    Mixed project (Python + JS) should require both pyproject.toml and package.json.
    """
    _touch(tmp_path / "src" / "app.py")
    _touch(tmp_path / "web" / "index.js")
    _touch(tmp_path / CI_SENTINEL)
    _touch(tmp_path / ".pre-commit-config.yaml")

    result = audit(tmp_path)

    assert "pyproject.toml" in result.missing_required
    assert "package.json" in result.missing_required


def test_mixed_python_and_c_requires_union(tmp_path: Path) -> None:
    """
    Mixed project (Python + C/C++) should require both pyproject.toml and a C/C++ build file.
    """
    _touch(tmp_path / "src" / "app.py")
    _touch(tmp_path / "native" / "main.c")
    _touch(tmp_path / CI_SENTINEL)
    _touch(tmp_path / ".pre-commit-config.yaml")

    result = audit(tmp_path)

    assert "pyproject.toml" in result.missing_required
    assert any(m in result.missing_required for m in {"CMakeLists.txt", "Makefile"})
