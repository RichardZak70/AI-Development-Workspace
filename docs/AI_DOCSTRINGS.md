# AI Docstrings Standard (Google Style)

This repository enforces **Google-style docstrings** for all Python code.

Docstrings are not optional. If Ruff fails, the change is not acceptable.

---

## Enforcement

Docstrings are enforced by:

- **Ruff** (`D` rules via `pydocstyle`)
- **Pre-commit** (fails locally before commit)
- **CI** (fails on pull requests)

Configuration source of truth:

- `pyproject.toml` → `[tool.ruff.lint]` and `[tool.ruff.lint.pydocstyle]`

---

## Required Format

Use Google-style sections:

- `Args:` for parameters
- `Returns:` for return value
- `Raises:` for exceptions
- Optional: `Attributes:` for class attributes

### General rules

- First line: **imperative, concise** summary.
- Blank line after summary if additional detail exists.
- Describe behavior and constraints, not implementation trivia.
- Types belong in type hints, not duplicated in docstrings (unless necessary for clarity).
- Every `Raises:` entry must correspond to a real raised exception path.

---

## Module Docstrings

Every module must have a docstring at the top.

```python
"""Utilities for prompt hashing and trace output emission."""
```

If the module is an executable script, include usage notes:

```python
"""Hash merged prompts and emit trace artifacts.

Usage:
    python scripts/hash_prompts.py --prompt-id <id>
"""
```

---

## Function Docstrings

```python
def hash_prompt(prompt: dict[str, object]) -> str:
    """Compute the SHA-256 hash of a normalized prompt object.

    Args:
        prompt: Prompt dictionary after normalization.

    Returns:
        Hex-encoded SHA-256 digest.
    """
```

Include `Raises:` when relevant:

```python
def load_yaml(path: Path) -> dict[str, object]:
    """Load a YAML file as a dictionary.

    Args:
        path: Path to the YAML file.

    Returns:
        Parsed YAML mapping.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the YAML root is not a mapping.
    """
```

---

## Class Docstrings

Use class docstrings to describe the purpose and invariants.

```python
class PromptHasher:
    """Deterministically hash prompt configurations.

    This class normalizes prompt objects to ensure stable hashing across runs.
    """
```

If the class has important attributes, include `Attributes:`.

```python
class AuditResult:
    """Represent the outcome of an audit.

    Attributes:
        target: Filesystem path audited.
        is_compliant: True if all required checks passed.
    """
```

---

## Method Docstrings

Public methods must have docstrings. Private methods must also have docstrings under strict policy unless explicitly exempted by repository policy.

```python
def run(self) -> int:
    """Run the audit and return a process exit code.

    Returns:
        0 if compliant; 1 otherwise.
    """
```

---

## How to Comply Quickly (Workflow)

### Generate a docstring skeleton (optional)

Use a VS Code extension such as autoDocstring (developer convenience only).

### Run checks locally

```bash
pre-commit run --all-files
# or
ruff check .
```

---

## Non-negotiables

- Docstrings must match the code.
- Docstrings must not claim behavior that is not implemented.
- If a function changes behavior, update its docstring in the same change.

---

## Where these belong in AI-Core-Standards

- `pyproject.toml`: repo root
- `.pre-commit-config.yaml`: repo root
- `docs/AI_DOCSTRINGS.md`: under `docs/` and referenced from README and/or `docs/LINTING_AND_CI_STANDARDS.md`
