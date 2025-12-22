# AI Core Standards

This repository centralizes the conventions, templates, and tooling that govern AI-focused initiatives across the organization. Use it as the canonical rulebook for designing, building, and auditing AI projects of any size.

## What Is Inside

- **docs/** – authoritative standards for prompts, structure, data, schemas, linting, and reviews.
- **templates/** – starter configs (prompts/models), editor settings, and data layouts.
- **scripts/** – audit and validation tooling:
  - `audit_ai_project.py` for structure;
  - `ajv-validate.mjs` for schema checks;
  - `validate_config.py` for Pydantic + JSON Schema validation with `--json` output;
  - `fix_audit_findings.py` to orchestrate audits with cross-repo support;
  - additional scripts for prompt extraction/merging, LLM usage, data layout, tooling, docs, and a consolidated check.
- **LICENSE** – usage terms for the entire standard set.

## Getting Started

1. Read `docs/PROJECT_STRUCTURE.md` and `docs/AI_PROMPTING_STANDARDS.md` to understand required layout and prompting rules.
2. Install toolchain: Node 18+ (`npm ci`) and Python 3.11+ (see `.pre-commit-config.yaml` for hooks and `.venv` layout).
3. Copy `templates/` into new projects, tailoring configs while keeping documented defaults intact.
4. Run audits:
   - `python scripts/audit_ai_project.py` (structure);
   - `node scripts/ajv-validate.mjs` (schema);
   - `python scripts/validate_config.py --json` (schema + Pydantic);
   - `python scripts/fix_audit_findings.py --run --fail-on-missing` to orchestrate available audits in sequence.
5. For existing projects, add both the standards repo and the target repo to a multi-root workspace so Copilot can cross-reference standards when fixing findings.

## Quality Gates

The same checks run locally (pre-commit) and in CI:

- Python docstrings: `ruff` (PEP 257) + `interrogate` (coverage)
- Prose linting: `vale` (README.md + docs/)
- JS doc comments: `eslint` + `eslint-plugin-jsdoc` (scripts/**/*.mjs)

Run locally:

- Python deps: `python -m pip install -r requirements-dev.txt`
- Node deps: `npm ci`
- Everything: `pre-commit run --all-files`

> Treat this repository as a living artifact. Submit pull requests for any net-new rules, keeping the documentation, templates, and automation in sync.
