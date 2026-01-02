# Standards Scope and Intent

## Purpose

AI-Core-Standards defines the canonical governance, structure, and enforcement rules for AI-enabled software projects.

It exists to ensure that AI-assisted development remains deterministic, auditable, model-agnostic, and maintainable over time.

This repository is a standards authority, not an application or project starter.

---

## In Scope

AI-Core-Standards governs:

- Project structure requirements
- Prompt definition, merging, and traceability
- Schema-first configuration and validation
- Data organization and provenance
- Audit and compliance tooling
- Documentation expectations for AI projects
- Tool-agnostic AI governance rules

All rules in this repository are intended to be machine-enforceable or directly tied to enforcement tooling.

---

## Out of Scope

AI-Core-Standards does not define:

- Application logic
- Product requirements
- Business workflows
- IDE-specific behavior (Copilot, Continue, Windsurf)
- Operating-system-specific conventions
- Language-specific coding style beyond linting interfaces
- End-user documentation or tutorials

These concerns belong in downstream project repositories or thin project templates.

---

## Intended Usage

This repository is intended to be consumed in one or more of the following ways:

- Referenced as a public standard
- Included as a Git submodule in project repositories
- Used as an audit and validation dependency
- Used as a reference when building project templates

It is not intended to be copied verbatim into application repositories.

---

## Relationship to Templates

Templates that support specific languages, tools, or workflows:

- Must adapt to AI-Core-Standards
- Must not override or weaken its rules
- May add stricter constraints

AI-Core-Standards remains the single source of truth.

---

## Change Policy

Changes to this repository are considered standards changes.

Any modification must:

- Preserve tool neutrality
- Maintain or strengthen enforcement
- Update documentation, schemas, and audits together
- Avoid introducing project-specific or tool-specific assumptions

If a rule cannot be enforced or audited, it does not belong here.

---

## Summary

AI-Core-Standards exists to define what must be true for AI-enabled projects, regardless of tools, models, or workflows.

Projects may vary.
Standards must not.

---

## Why This File Exists

This document:

- Prevents the repository from drifting into a template
- Explains why tool-specific configuration is excluded
- Gives AI agents a clear refusal boundary
- Complements docs/AI_GOVERNANCE_RULES.md without duplicating it

Together, docs/STANDARDS_SCOPE.md and docs/AI_GOVERNANCE_RULES.md form the constitutional layer of AI-Core-Standards.
