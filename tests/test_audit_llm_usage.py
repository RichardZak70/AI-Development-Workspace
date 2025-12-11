import importlib
import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

mod = importlib.import_module("audit_llm_usage")
audit = getattr(mod, "audit")
RAW_LLM_PATTERNS = getattr(mod, "RAW_LLM_PATTERNS")
SCAN_EXTENSIONS = getattr(mod, "SCAN_EXTENSIONS")
IGNORE_DIRS: set[str] = set(getattr(mod, "IGNORE_DIRS", set()))


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_compliant_when_no_raw_calls(tmp_path: Path) -> None:
    code = """from client import llm
resp = llm.invoke(prompt_id="hello")
"""
    _write(tmp_path / "src" / "app.py", code)

    result = audit(tmp_path)

    assert result.is_compliant is True
    assert result.findings == []


def test_flags_raw_openai_call(tmp_path: Path) -> None:
    code = """import openai
resp = openai.ChatCompletion.create(model="gpt-4", messages=[])
"""
    _write(tmp_path / "service" / "llm.py", code)

    result = audit(tmp_path)

    assert result.is_compliant is False
    assert any("ChatCompletion" in f.message for f in result.findings)
    assert any("service/llm.py" in f.path for f in result.findings)
    if hasattr(result.findings[0], "snippet"):
        assert any("openai.ChatCompletion.create" in (f.snippet or "") for f in result.findings)


def test_flags_raw_azure_call(tmp_path: Path) -> None:
    code = """from azure.ai import openai
resp = client.chat.completions.create(model="gpt-4o", messages=[])
"""
    _write(tmp_path / "service" / "azure_llm.py", code)

    result = audit(tmp_path)

    assert result.is_compliant is False
    azure_pattern = next(
        (msg for pat, msg in RAW_LLM_PATTERNS if "client.chat.completions.create" in pat),
        None,
    )
    if azure_pattern is not None:
        assert any(azure_pattern in f.message for f in result.findings)
    else:
        assert any("Raw" in f.message for f in result.findings)


def test_json_round_trip(tmp_path: Path) -> None:
    code = """import openai
resp = openai.Completion.create(model="gpt-3", prompt="hi")
"""
    _write(tmp_path / "main.py", code)

    result = audit(tmp_path)
    payload = result.to_json()
    serialized = json.loads(json.dumps(payload))

    assert "is_compliant" in serialized
    assert "findings" in serialized
    assert isinstance(serialized["findings"], list)
    assert serialized["is_compliant"] is False
    assert serialized["findings"]


def test_only_scans_known_extensions(tmp_path: Path) -> None:
    _write(tmp_path / "notes" / "llm.txt", "openai.ChatCompletion.create()")
    _write(tmp_path / "src" / "llm.py", "print('ok')")

    result = audit(tmp_path)

    # txt should be ignored; py with no pattern should be clean
    assert result.is_compliant is True
    assert result.findings == []


def test_skips_ignored_directories(tmp_path: Path) -> None:
    if not IGNORE_DIRS:
        pytest.skip("IGNORE_DIRS not defined in audit_llm_usage module.")

    ignored_dir = next(iter(IGNORE_DIRS))
    _write(tmp_path / ignored_dir / "llm.py", "openai.ChatCompletion.create()")
    _write(tmp_path / "src" / "ok.py", "print('hi')")

    result = audit(tmp_path)

    assert result.is_compliant is True
    assert result.findings == []


def test_respects_max_size_bytes(tmp_path: Path) -> None:
    big_file = tmp_path / "src" / "big.py"
    big_file.parent.mkdir(parents=True, exist_ok=True)
    big_file.write_bytes(b"#" * (2_000_000))
    _write(tmp_path / "src" / "small.py", "openai.ChatCompletion.create()")

    result = audit(tmp_path, max_size_bytes=1_000_000)  # type: ignore[arg-type]

    assert any("small.py" in f.path for f in result.findings)
    assert not any("big.py" in f.path for f in result.findings)


def test_patterns_exposed_for_coverage() -> None:
    # Ensure exported patterns/extensions are non-empty for sanity
    assert RAW_LLM_PATTERNS
    assert SCAN_EXTENSIONS
