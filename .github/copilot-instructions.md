# Copilot Instructions (Authoritative)

These instructions apply to all AI-assisted changes in this repository.

You are updating the AI-Governed-Desktop-Template repo to be strictly compliant with AI-Core-Standards.

Non-negotiables:

- AI-Core-Standards is authoritative.
- The template must remain generic (no Shine-AI/product-specific language).
- Canonical configs must be schema-validated in CI.
- Prefer thin wrapper docs that link to tools/AI-Core-Standards/docs/ rather than duplicating content.

Tasks (in order):

1. Docs compliance (match AI-Core audit_docs.py required list):

- Add these missing docs as thin wrappers that link to the authoritative AI-Core docs in tools/AI-Core-Standards/docs/:
  docs/STANDARDS_SCOPE.md
  docs/AI_PROMPTING_STANDARDS.md
  docs/DATA_ORGANIZATION.md
  docs/SCHEMAS_AND_VALIDATION.md
  docs/LINTING_AND_CI_STANDARDS.md
  docs/AI_PROJECT_REVIEW_CHECKLIST.md
- Add recommended docs/STATUS.md (short).
- Update README.md to link all required docs including docs/PROJECT_STRUCTURE.md and docs/COPILOT_USAGE.md.

2. Remove Shine-AI specificity:

- Edit docs/COPILOT_USAGE.md and docs/DEVELOPMENT.md to remove “Shine-AI” references.
- Generalize “Studio Mode” wording as an optional pattern (not a built-in template feature).
- Ensure docs describe only what exists in the template.

3. Canonical config alignment:

- Rename the current prompt layer registry file:
  config/prompts.yaml -> config/prompts.layers.yaml
- Make config/prompts.yaml be AI-Core prompt definitions format (prompt_id -> {description, system, user_template, output_format?}).
- Update config/prompts.core.yaml, prompts.defaults.yaml, prompts.custom.yaml to use the same AI-Core prompt-definition format so they can be merged deterministically.
- Update src/app_core/prompt_layers.py and scripts/tools/check_ai_rules.py to use config/prompts.layers.yaml as the registry and output to config/prompts.yaml.
- Rename config/eval.yaml -> config/evals.yaml and convert content to AI-Core eval_config schema (minimal smoke eval is fine).
- Replace config/models.yaml and config/project.yaml with AI-Core minimal schema-compliant shapes. If extra routing is needed later, put it in a separate ext file with its own schema.

4. Validation & CI enforcement:

- Update scripts/ajv-validate.mjs to validate:
  config/project.yaml, config/models.yaml, config/prompts.yaml, config/evals.yaml
  against the authoritative schemas in tools/AI-Core-Standards/schemas/.
- Add a CI step that runs:
  python tools/AI-Core-Standards/scripts/audit_docs.py --target-root .
- Ensure README includes a bootstrap step:
  git submodule update --init --recursive

5. Tests:

- Update/extend tests to cover the new prompt merge output file name and schema validity.
- Ensure pytest, CI, and all linters pass.

Deliverables:

- Provide the diff across files (or implement directly).
- Keep the template thin and generic.
- Do not introduce new product features.
