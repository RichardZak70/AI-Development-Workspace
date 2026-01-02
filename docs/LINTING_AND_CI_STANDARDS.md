# Linting and CI Standards

Every project must:

- Have at least one linter + formatter appropriate to the language.
- Run tests + linting in CI on every push and pull request.

Language-specific tools (examples):

- Python: Ruff + mypy + pytest
- TypeScript: ESLint + Prettier + Jest
- C/C++: clang-tidy + clang-format + ctest

Each template repo is responsible for implementing concrete tooling.
This core doc defines the **requirement**, not the specific choice per language.

## Python docstrings (required)

For Python, this repo enforces **Google-style docstrings** using Ruff.

See: `docs/AI_DOCSTRINGS.md`

## Config YAML documentation (required)

Config YAML files are part of the project contract and must be validated in CI.

- `config/prompts.yaml`: every prompt entry must include a non-empty `description`.
- `config/evals.yaml`: every eval entry must include a non-empty `description`.
- `config/project.yaml`: must include a non-empty `description`.

This repo enforces these requirements via JSON Schema + a validator script (see `scripts/validate_config.py`) and runs it in pre-commit for `config/**` and `templates/config/**`.
