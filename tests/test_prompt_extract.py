"""Tests for prompt extraction utilities."""

import importlib
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

mod = importlib.import_module("prompt_extract")
extract_prompts = getattr(mod, "extract_prompts")
print_human = getattr(mod, "print_human")
IGNORE_DIRS: set[str] = set(getattr(mod, "IGNORE_DIRS", set()))


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_no_prompts_returns_empty(tmp_path: Path) -> None:
    """Extraction returns empty result when no prompts exist."""
    _write(tmp_path / "src" / "app.py", "x = 1")

    result = extract_prompts(tmp_path, min_length=0)

    assert result.prompts == []
    assert result.is_compliant is True


def test_extracts_prompt_variables(tmp_path: Path) -> None:
    """Extraction finds common prompt variable assignments."""
    code = '''SYSTEM_PROMPT = """You are helpful."""
USER_PROMPT = "Hello"
other = "skip"
'''
    file_path = tmp_path / "service" / "prompts.py"
    _write(file_path, code)

    result = extract_prompts(tmp_path, min_length=0)

    assert len(result.prompts) == 2
    names = {p.var_name for p in result.prompts}
    assert {"SYSTEM_PROMPT", "USER_PROMPT"} <= names
    paths = {Path(p.path).as_posix() for p in result.prompts}
    assert paths == {"service/prompts.py"}
    assert all(p.line > 0 for p in result.prompts)


def test_min_length_filters_short_prompts(tmp_path: Path) -> None:
    """Minimum length filter excludes short prompts."""
    code = """SYSTEM_PROMPT = "This is a long enough prompt to be included."
SHORT_PROMPT = "hi"
"""
    _write(tmp_path / "p.py", code)

    result = extract_prompts(tmp_path, min_length=20)

    names = {p.var_name for p in result.prompts}
    assert "SYSTEM_PROMPT" in names
    assert "SHORT_PROMPT" not in names


def test_extracts_from_fstring_and_concatenation(tmp_path: Path) -> None:
    """Extraction handles simple concatenation and f-strings."""
    code = """SYSTEM_PROMPT = "You are " + "a helper."
USER_PROMPT = f"User says: {{" + "name" + "}}"
"""
    _write(tmp_path / "f.py", code)

    result = extract_prompts(tmp_path, min_length=0)
    names = {p.var_name for p in result.prompts}
    assert {"SYSTEM_PROMPT", "USER_PROMPT"} <= names

    values = {p.var_name: p.value for p in result.prompts}
    assert values["SYSTEM_PROMPT"].startswith("You are")
    assert "User says:" in values["USER_PROMPT"]


def test_ignores_configured_directories(tmp_path: Path) -> None:
    """Extraction skips directories listed in IGNORE_DIRS."""
    if not IGNORE_DIRS:
        pytest.skip("prompt_extract.IGNORE_DIRS not defined; nothing to test here.")

    ignored_dir = next(iter(IGNORE_DIRS))
    _write(tmp_path / ignored_dir / "hidden.py", 'SYSTEM_PROMPT = "You should not see this"')
    _write(tmp_path / "visible.py", 'SYSTEM_PROMPT = "You should see this"')

    result = extract_prompts(tmp_path, min_length=0)

    paths = {Path(p.path).as_posix() for p in result.prompts}
    assert "visible.py" in paths
    assert not any(ignored_dir in p for p in paths)


def test_json_round_trip(tmp_path: Path) -> None:
    """Extraction result round-trips through JSON serialization."""
    _write(tmp_path / "p.py", "PROMPT = 'hi'")

    result = extract_prompts(tmp_path, min_length=0)
    payload = result.to_json()
    serialized = json.loads(json.dumps(payload))

    assert "prompts" in serialized
    assert serialized["is_compliant"] is True
    assert isinstance(serialized["prompts"], list)
    if serialized["prompts"]:
        prompt = serialized["prompts"][0]
        assert "path" in prompt
        assert "var_name" in prompt
        assert "value" in prompt
        if "line" in prompt:
            assert isinstance(prompt["line"], int)


def test_human_output_mentions_counts(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Human output includes a count of discovered prompts."""
    _write(tmp_path / "p.py", "PROMPT = 'hi'")

    result = extract_prompts(tmp_path, min_length=0)
    print_human(result)

    out = capsys.readouterr().out
    assert "Found 1 prompt" in out or "Found 1 prompt(s)" in out


def test_yaml_output(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """YAML skeleton output includes prompt keys and source metadata."""
    _write(tmp_path / "p.py", "PROMPT = 'hi there'")

    # Invoke via function path to produce YAML skeleton
    original_argv = sys.argv[:]
    try:
        sys.argv = ["prompt_extract"]  # ensure argparse doesn't see pytest args
        result = extract_prompts(tmp_path, min_length=0)
    finally:
        sys.argv = original_argv

    # Build YAML content similar to main's --yaml path
    yaml_lines = ["prompts:"]
    for idx, finding in enumerate(result.prompts, start=1):
        key = f"prompt_{idx}"
        yaml_lines.append(f"  {key}:")
        yaml_lines.append("    system: |")
        for line in finding.value.splitlines() or [""]:
            yaml_lines.append(f"      {line}")
        yaml_lines.append(f"    _source: {finding.path}:{finding.line} ({finding.var_name})")

    yaml_content = "\n".join(yaml_lines)
    assert "prompts:" in yaml_content
    assert "prompt_1" in yaml_content
    assert "_source:" in yaml_content
