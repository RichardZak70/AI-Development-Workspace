# AI Governance Rules (Authoritative)

## Purpose

This document defines how AI systems, agents, and assistants are permitted to interact with this repository.

AI-Core-Standards is a governance and standards authority, not an application or product repository.
These rules exist to prevent drift, ambiguity, and tool-specific lock-in while enabling safe AI-assisted evolution of the standards.

All AI-generated contributions must comply with these rules.

---

## Scope

These rules apply to:

- AI tools (Copilot, Continue, Claude, MCP servers, CI agents)
- Human-AI collaborative workflows
- Automated scripts that generate or modify content

These rules do not define how downstream projects must behave.
Downstream repositories may impose stricter rules, but never weaker ones.

---

## Authority Model (Non-Negotiable)

### Canonical Sources

The following sources define truth, in descending order of authority:

1. Schemas (`schemas/`)
   - Machine-readable contracts
   - Enforced by validation and audits
2. Audit scripts (`scripts/`)
   - Enforce compliance with standards
3. Documentation (`docs/`)
   - Normative descriptions of rules and intent
4. Templates (`templates/`)
   - Reference defaults only
   - Never authoritative

AI must never treat templates or examples as canonical over schemas or audits.

---

## What This Repository Is Not

AI must not reinterpret this repository as:

- A project starter template
- A demo or example application
- A tool-specific configuration repository
- A place for project-level rules or OS-specific constraints

Any contribution that shifts the repository toward those roles must be rejected.

---

## Change Discipline (Critical)

AI must treat standards changes as contract changes.

### Required Coupling

If an AI modifies any of the following, it must also update the corresponding items.

| Change | Must Update |
|------|-------------|
| Prompt definitions | Prompt schema, validation, docs |
| Schemas | Validators, audits, docs |
| Audit logic | Tests, docs |
| Templates | Docs explaining intended usage |
| Validation rules | CI expectations, docs |

Partial updates are forbidden.

---

## Prompt Governance Rules

- YAML prompt files are the only canonical prompt sources
- Markdown prompt files, if any, are illustrative examples only
- Prompts must:
  - have stable IDs
  - be mergeable
  - be hashable
  - be traceable to outputs
- AI must never inline prompt text into code as a substitute for governed prompts

Any AI change that bypasses prompt governance is invalid.

---

## Tool Neutrality

AI-Core-Standards must remain tool-agnostic.

AI must not:

- Introduce tool-specific behavior
- Assume VS Code usage
- Require IDE-specific file paths for compliance

Tool integrations belong in downstream templates, not here.

---

## Forbidden Actions

AI must refuse to:

- Introduce undocumented rules
- Add configuration without schema coverage
- Add examples that contradict standards
- Weaken existing enforcement
- Modify audits to pass invalid structures
- Change semantics without explicit justification

Silently changing meaning is forbidden.

---

## AI Behavior Expectations

When generating or modifying content, AI must:

- Prefer minimal, atomic changes
- Explain why a change is required
- Preserve existing structure and intent
- Avoid speculative or convenience-driven edits
- Treat this repository as a specification, not a sandbox

If a requested change violates these expectations, AI must explicitly refuse and explain why.

---

## Relationship to Downstream Repositories

- AI-Core-Standards defines the rules
- Downstream repositories adapt to them
- This repository does not adapt to project needs

Downstream repositories may:

- Add project-specific AI rules
- Add tool integrations

Downstream repositories may not weaken or override this repository's standards.

---

## Enforcement

These rules are enforced through:

- Schema validation
- Audit scripts
- CI checks
- Human review

If AI-generated changes break enforcement, they are invalid and must be regenerated.

---

## Summary (For AI Systems)

This repository enforces:

- Schema-first governance
- Audit-backed standards
- Prompt determinism
- Tool neutrality
- Explicit change discipline

If a change cannot be enforced, audited, and documented, it does not belong here.
