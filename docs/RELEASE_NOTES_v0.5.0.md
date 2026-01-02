# AI-Core-Standards v0.5.0 Release Notes

## Highlights

- Adds a constitutional governance layer with explicit scope and AI interaction rules.
- Consolidates and documents quality gates that run locally and in CI (Python, Node, docs, schemas).
- Reinforces schema-first configuration validation across Node (AJV) and Python (Pydantic models).
- Maintains tool neutrality: standards remain independent of any specific IDE or AI tool.

## What's Included

### Docs

- Governance and scope:
  - [docs/AI_GOVERNANCE_RULES.md](AI_GOVERNANCE_RULES.md)
  - [docs/STANDARDS_SCOPE.md](STANDARDS_SCOPE.md)
- Docstring standard for Python:
  - [docs/AI_DOCSTRINGS.md](AI_DOCSTRINGS.md)
- Canonical standards already present in this repo:
  - [docs/PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)
  - [docs/AI_PROMPTING_STANDARDS.md](AI_PROMPTING_STANDARDS.md)
  - [docs/DATA_ORGANIZATION.md](DATA_ORGANIZATION.md)
  - [docs/SCHEMAS_AND_VALIDATION.md](SCHEMAS_AND_VALIDATION.md)
  - [docs/LINTING_AND_CI_STANDARDS.md](LINTING_AND_CI_STANDARDS.md)
  - [docs/AI_PROJECT_REVIEW_CHECKLIST.md](AI_PROJECT_REVIEW_CHECKLIST.md)

### Schemas

- JSON Schema (Draft 2020-12) coverage for core configuration contracts in `schemas/`, including:
  - [schemas/models.schema.json](../schemas/models.schema.json)
  - [schemas/prompts.schema.json](../schemas/prompts.schema.json)
  - [schemas/eval_config.schema.json](../schemas/eval_config.schema.json)
  - [schemas/outputs_metadata.schema.json](../schemas/outputs_metadata.schema.json)

### Scripts

- Audits and consolidated checks in `scripts/`:
  - Structure: [scripts/audit_ai_project.py](../scripts/audit_ai_project.py)
  - Docs linkage: [scripts/audit_docs.py](../scripts/audit_docs.py)
  - Data layout and trace metadata: [scripts/audit_data_layout.py](../scripts/audit_data_layout.py)
  - Tooling/CI presence: [scripts/audit_tooling.py](../scripts/audit_tooling.py)
  - Raw LLM call detection: [scripts/audit_llm_usage.py](../scripts/audit_llm_usage.py)
  - Consolidated runner: [scripts/rz_ai_check.py](../scripts/rz_ai_check.py)
- Config validation tooling:
  - Node/AJV: [scripts/ajv-validate.mjs](../scripts/ajv-validate.mjs)
  - Python/Pydantic: [scripts/validate_config.py](../scripts/validate_config.py)
- Prompt utilities:
  - [scripts/prompt_extract.py](../scripts/prompt_extract.py)
  - [scripts/prompt_merge.py](../scripts/prompt_merge.py)
  - [scripts/migrate_prompts_from_code.py](../scripts/migrate_prompts_from_code.py)

### CI

- GitHub Actions workflow: `.github/workflows/ci.yml`

  - Workflow file: [.github/workflows/ci.yml](../.github/workflows/ci.yml)
  - Runs Node-based schema validation and markdown linting.
  - Runs Python linting, docstring structure checks, typing checks, and tests.
  - Runs prose linting using `python scripts/run_vale.py`.

## Upgrade Notes (Downstream Repositories)

If you consume AI-Core-Standards as a Git submodule:

1. Update the submodule to the `v0.5.0` tag in your normal workflow.
2. Re-run audits against your target repository and remediate any new findings.
3. Treat `schemas/` and `scripts/` as authoritative.
   - Do not copy this repository into your application repository.
   - Prefer referencing it or auditing against it.

## Verification

Run these commands from the repo root.

### Node

- Install dependencies: `npm ci`
- Validate docs + schemas: `npm run validate:all`

### Python

- Install dev dependencies: `python -m pip install -r requirements-dev.txt`
- Run tests: `python -m pytest -q`

### Full Local Gate (Optional)

- Run all pre-commit hooks: `pre-commit run --all-files`

## Compatibility

- Node:
  - CI uses Node 20.
  - `package.json` declares `engines.node` as `>=18`.
- Python:
  - CI uses Python 3.11.
  - Ruff configuration targets `py311`.
