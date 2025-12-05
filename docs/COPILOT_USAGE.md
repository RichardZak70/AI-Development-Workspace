# Copilot Usage Standard

Copilot is a **code completion tool**, not a free-form reasoning engine.
To get consistent behavior:

- Use structured "Copilot Instruction" comments immediately above the code.
- Use different patterns for:
  - new code,
  - refactoring,
  - debugging,
  - documentation.

## New code

```python
# Copilot Instruction:
# Role: Senior engineer.
# Objective: Implement the function below.
# Constraints:
# - Follow project style (PEP 8 for Python).
# - Include type hints and a concise docstring.
# - No external dependencies unless necessary.
# Output: Only the function code.

def ...
```

## Debugging

```text
# Copilot Instruction:
# Debug this function.
# Error:
# {paste error}
# Requirements:
# - Identify root cause.
# - Propose minimal fix.
# - Output corrected function only.
```

## Refactoring

```text
# Copilot Instruction:
# Refactor for clarity and maintainability without changing external behavior.
# Keep: same function signature and return types.
# Improve: naming, structure, readability, duplication.
```

Every repo should either link to this doc or adapt it into a project-local `docs/COPILOT.md`.
