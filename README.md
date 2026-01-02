# AI Core Standards

Opinionated core standards, schemas, and audits for production-grade AI-assisted software projects.

This repository is the canonical rulebook and enforcement layer for designing, building, and auditing AI projects of any size.
It exists to prevent the most common failure mode in AI development: unstructured, non-auditable systems that collapse as they grow.

AI Core Standards defines what “done right” means for prompts, models, data, evaluations, tooling, and documentation—and provides automated audits to enforce it.

This repository is not a project template and should not be copied verbatim into application repos.
It is intended to be referenced, audited against, or included as a submodule.

## Why This Exists

Most AI projects fail after the demo.

Not because the model is wrong—but because everything around the model is unstructured.

Common failure modes this repository explicitly prevents:

- Prompts buried in code with no versioning or review
- Silent model changes with no audit trail
- Outputs that cannot be traced back to inputs, prompts, or configs
- Ad-hoc evaluation scripts that can’t be repeated
- AI-generated codebases that no one can safely modify six weeks later

AI Core Standards exists to eliminate those failure modes.

This repository enforces a simple rule:

If an AI system cannot be audited, reproduced, or explained, it is not production-ready.

To make that practical, the standards here:

- Treat prompts, models, evaluations, and data layouts as first-class configuration
- Define schemas so “valid” is machine-checkable
- Provide audits so compliance is provable, not aspirational
- Separate governance (core standards) from implementation (project templates)

This is not about style.
This is about preventing AI-assisted projects from collapsing under their own entropy.

## What This Repository Is (and Is Not)

This is:

- A governance framework for AI-assisted development
- A set of enforceable standards backed by schemas and audits
- A cross-language foundation (Python, Node, TS, C/C++)
- A control plane for prompt, model, and data discipline

This is not:

- A framework (no runtime lock-in)
- A boilerplate app or starter project
- A single “one-size-fits-all” template

## Repository Contents

## Architecture Overview

AI Core Standards is designed as a control plane, not a framework.

```text
┌──────────────────────────────────────────────┐
│              AI CORE STANDARDS               │
│  (Governance & Enforcement – This Repo)      │
│                                              │
│  ┌───────────────┐   ┌────────────────────┐  │
│  │ docs/         │   │ schemas/           │  │
│  │ - rules       │   │ - prompts          │  │
│  │ - structure   │   │ - models           │  │
│  │ - reviews     │   │ - evals            │  │
│  │               │   │ - outputs metadata │  │
│  └───────────────┘   └────────────────────┘  │
│                                              │
│  ┌────────────────────────────────────────┐  │
│  │ scripts/                               │  │
│  │ - audits (structure, data, docs, LLM)  │  │
│  │ - validators (AJV, Pydantic)           │  │
│  │ - prompt extract / merge               │  │
│  │ - consolidated checks                  │  │
│  └────────────────────────────────────────┘  │
└──────────────────────────────────────────────┘
                    ▲
                    │ enforced by
                    │ audits + schemas
                    │
┌──────────────────────────────────────────────┐
│              PROJECT TEMPLATES               │
│        (Thin, Type-Specific Overlays)        │
│                                              │
│  python-cli | python-service | node-cli | …  │
│                                              │
│  - minimal skeleton                          │
│  - language/tooling defaults                 │
│  - references core standards                 │
└──────────────────────────────────────────────┘
                    ▲
                    │ applied to
                    │
┌──────────────────────────────────────────────┐
│                AI PROJECTS                   │
│        (Your Actual Repositories)            │
│                                              │
│  - business logic                            │
│  - models + prompts (config/)                │
│  - data + outputs (data/)                    │
│  - evaluations                               │
│                                              │
│  Audited continuously against core rules     │
└──────────────────────────────────────────────┘
```

### docs/

Authoritative, human-readable standards. These define the rules audits enforce.

- Prompting standards
- Project structure
- Data organization & traceability
- Schema & validation philosophy
- Linting and CI expectations
- AI project review checklist

### schemas/

JSON Schemas that formalize AI configuration and artifacts:

- Models (`models.schema.json`)
- Prompts (`prompts.schema.json`)
- Evaluations (`eval_config.schema.json`)
- Run outputs / metadata (`outputs_metadata.schema.json`)
- (Optional) project-level metadata and future extensions

These schemas are consumed by both Node (AJV) and Python (Pydantic) validators.

### templates/

Baseline reference artifacts, not full applications:

- Canonical `config/` examples (models, prompts)
- Standard data layout
- Minimal files intended to be overlaid by project templates

Templates here are intentionally thin and framework-agnostic.

### scripts/

Audit, validation, and migration tooling, including:

- `audit_ai_project.py` – core structure compliance
- `audit_data_layout.py` – data layout & output traceability
- `audit_docs.py` – documentation presence & README linkage
- `audit_llm_usage.py` – detection of raw / non-standard LLM calls
- `audit_tooling.py` – CI, linting, and language-aware tooling checks
- `ajv-validate.mjs` – JSON Schema validation (Node/AJV)
- `validate_config.py` – JSON Schema + Pydantic validation (Python)
- `prompt_extract.py` – extract inline prompts from code
- `prompt_merge.py` – merge core/template/project prompt layers
- `rz_ai_check.py` – consolidated audit runner
- `fix_audit_findings.py` – orchestrate audits and guide remediation

### LICENSE

Usage terms for the entire standards set.

## Key Design Principles

- Core Standards are immutable from the project’s point of view
  - Projects conform to them; they do not fork them.
- Templates are thin
  - They help you start, not redefine rules.
- Audits are the source of truth
  - “Looks fine” is irrelevant.
  - If the audit fails, the project is non-compliant.

## Mental Model (Important)

Think of this system like ISO standards + automated inspectors:

- Docs = the written standard
- Schemas = the formal specification
- Audits = the inspectors
- Templates = convenience tooling, not authority

This is why the repo scales across:

- languages,
- frameworks,
- deployment models,
- and AI providers.

## Getting Started

### New Projects

Read:

- `docs/AI_GOVERNANCE_RULES.md`
- `docs/STANDARDS_SCOPE.md`
- `docs/PROJECT_STRUCTURE.md`
- `docs/AI_PROMPTING_STANDARDS.md`
- `docs/AI_DOCSTRINGS.md`

Choose an appropriate project template / archetype (CLI, service, library, RAG app, hardware-facing app).

Overlay template files while keeping core standards intact.

Validate early:

```bash
python scripts/rz_ai_check.py
```

### Existing Projects

Add this repository alongside the target project in a multi-root workspace.

Run audits:

```bash
python scripts/audit_ai_project.py
node scripts/ajv-validate.mjs
python scripts/validate_config.py --json
python scripts/rz_ai_check.py --target-root <path>
```

Use Copilot with the standards repo open to fix findings against canonical rules, not guesses.

Re-run audits until compliant.

## Quality Gates

The same checks are expected to run locally and in CI.

### Tooling

- Python: ruff, mypy, pytest
- Node/TS: eslint, tsc --noEmit
- Docs: vale, markdownlint
- Configs: yamllint, JSON Schema (AJV)

### Run Everything Locally

```bash
npm ci
python -m pip install -r requirements-dev.txt
pre-commit run --all-files
```

## Design Philosophy

- Structure beats cleverness
- Prompts are configuration, not inline strings
- Every output must be traceable
- Schemas first, code second
- Audits define “done”

If an AI system cannot be audited, reproduced, or explained, it is not production-ready.

## Contributing

Treat this repository as a living standard.

Any new rule must include:

- Documentation
- Schema updates (if applicable)
- Audit logic

Keep docs, templates, and automation in sync.

Submit PRs with a clear rationale: what failure mode does this prevent?
