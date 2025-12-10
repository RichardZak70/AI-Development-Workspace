# Using Copilot to Fix Audit Findings

The following instruction blocks are templates to use when fixing issues reported by the AI-Core-Standards audits.

For each audit type:

1. Run the audit script.
2. Open the relevant file(s).
3. Paste an appropriate Copilot Instruction block above the area you want changed.
4. Let Copilot generate the changes, then review.

---

## 1. Structure Audit (`audit_ai_project.py`)

Create missing folders/files and align layout.

Use this in `README.md` or a project notes file when aligning structure:

```text
# Copilot Instruction:
# Using the structure standard in ../RZ-AI-Core-Standards/docs/PROJECT_STRUCTURE.md
# and the output of scripts/audit_ai_project.py for THIS repo,
# do the following:
# - List which required directories and files are missing.
# - Propose a concrete plan to add them (paths + purpose).
# - Do not invent folders that are not in the standard; keep it aligned.

## Structure Alignment Plan
```

When creating a missing config file (e.g., `config/models.yaml`):

```text
# Copilot Instruction:
# Create a valid models.yaml for THIS project using
# ../RZ-AI-Core-Standards/templates/config/models.yaml as a reference.
# - Preserve this project's actual models and providers if they exist.
# - Otherwise, create a minimal, valid default that passes schema validation.
# - Do not copy unused or irrelevant sections from the template.
```

## 2. Config & Schema Validation (`ajv-validate.mjs`)

Fix invalid `models.yaml` or `prompts.yaml`.

Paste this at the top of the relevant YAML file:

```text
# Copilot Instruction:
# The ajv-validate script reports schema validation errors for this file.
# Using ../RZ-AI-Core-Standards/schemas/{schema_name}.schema.json
# and ../RZ-AI-Core-Standards/templates/config/{same_name}.yaml as references:
# - Fix only the fields that violate the schema.
# - Preserve project-specific values where possible.
# - Ensure the final file would pass schema validation.
# Do NOT remove keys just to silence errors unless they are truly unused.

# Existing content continues below...
```

If you have the error list from ajv-validate:

```text
# Copilot Instruction:
# Given these AJV validation errors for config/{file}.yaml:
# {paste ajv error output}
# and using ../RZ-AI-Core-Standards/schemas/{schema}.schema.json as the contract:
# - Propose the minimal set of changes needed to make the file valid.
# - Then rewrite the corrected YAML content.
```

## 3. Prompt Extraction & Normalization

Move inline prompts from code into `config/prompts.yaml`.

In `config/prompts.yaml`:

```text
# Copilot Instruction:
# Scan the source file src/{path/to/file}.{ext} for inline LLM prompts that
# describe behavior (system/user instructions).
# For each such prompt:
# - Create a new named prompt entry here following the existing schema
#   (description, system, user_template, output_format if needed).
# - Use a clear id like {context}_{purpose}, e.g., chat_support, code_debug_api.
# - Keep prompt text faithful to the original.
```

Back in the code file that had the inline prompt:

```text
# Copilot Instruction:
# Replace the inline prompt string(s) below with references to the named prompts
# you just added in config/prompts.yaml.
# Requirements:
# - Introduce or reuse a small helper to load prompts from config/prompts.yaml.
# - Use prompt_id-based lookup instead of hard-coded strings.
# - Do not change non-prompt logic.
```

## 4. Prompt Merging & Resolution (`prompt_merge.py`)

Define template-specific overrides and merge with core.

In a template repo `config/prompts.defaults.yaml`:

```text
# Copilot Instruction:
# Using ../RZ-AI-Core-Standards/templates/config/prompts.yaml as the base,
# create template-specific prompt overrides/additions for THIS template.
# - Add prompts that are specific to this template's domain (e.g. chatbot, hardware tools).
# - Do not duplicate generic prompts unless you need to override them.
# - Keep ids stable and descriptive.
```

In a project repo when preparing `config/prompts.custom.yaml`:

```text
# Copilot Instruction:
# Based on the actual prompts currently used in this project (search src/**),
# add project-specific prompts or overrides here.
# - Only override core/template prompts when behavior must change.
# - Otherwise add new ids.
# - Ensure everything here would pass the prompts.schema.json constraints.
```

In a docs file explaining merging:

```text
# Copilot Instruction:
# Summarize how prompt merging works in THIS project, assuming:
# - Core prompts from RZ-AI-Core-Standards/templates/config/prompts.yaml
# - Template defaults from config/prompts.defaults.yaml
# - Project overrides from config/prompts.custom.yaml
# Explain:
# - precedence order,
# - how conflicts are resolved,
# - how developers should add or override prompts.
```

## 5. LLM Usage Audit (`audit_llm_usage.py`)

Replace raw provider calls with standard clients and named prompts.

In a file with direct provider calls (e.g., `openai.ChatCompletion.create`):

```text
# Copilot Instruction:
# Replace the direct LLM API call(s) below with the standard client defined in
# src/llm/client_{provider}.py (or create it based on the core template if missing).
# Requirements:
# - All calls should pass a prompt_id and structured input, not raw strings.
# - The client should load prompts from config/prompts.yaml and models from config/models.yaml.
# - Do not change business logic other than wiring through the client.
```

To check that all call sites use valid prompt ids:

```text
# Copilot Instruction:
# For each call in this file that invokes the LLM client:
# - Verify the prompt_id exists in config/prompts.yaml.
# - If any are missing, propose new entries for prompts.yaml using
#   the core format from RZ-AI-Core-Standards/templates/config/prompts.yaml.
# - Do not invent behavior; derive prompt text from existing inline comments/logic.
```

## 6. Data Layout & Traceability Audit (`audit_data_layout.py`)

Move outputs into `data/` and enforce metadata.

In the pipeline or script that writes model outputs:

```text
# Copilot Instruction:
# Update this pipeline so that:
# - All LLM outputs are written under data/outputs/ in this repo.
# - Each output file name encodes: timestamp, model name, and prompt_id.
# - Each JSON output includes top-level metadata fields:
#   run_id, model, prompt_id, timestamp.
# Use the directory layout and guidance in ../RZ-AI-Core-Standards/templates/data_layout.txt.
# Do not alter the core business logic or data being processed.
```

In `docs/DATA_ORGANIZATION.md` (project-local):

```text
# Copilot Instruction:
# Using ../RZ-AI-Core-Standards/docs/DATA_ORGANIZATION.md as a reference,
# write a project-specific explanation of how THIS repo uses:
# - data/raw
# - data/processed
# - data/prompts
# - data/outputs
# - data/cache
# - data/embeddings
# Include at least one concrete example of a typical output file path and its metadata.
```

## 7. Tooling & CI Audit (`audit_tooling.py`)

Add or adapt pre-commit, linters, and CI.

In `.pre-commit-config.yaml`:

```text
# Copilot Instruction:
# Adapt the pre-commit configuration from ../RZ-AI-Core-Standards/templates/.pre-commit-config.yaml
# for THIS repository.
# - Enable Python hooks if Python code is present.
# - Enable JSON/YAML/Markdown hooks for config and docs.
# - Do not add hooks for languages that are not used here.
# - Keep the config minimal but standards-compliant.
```

In `.github/workflows/ci.yml`:

```text
# Copilot Instruction:
# Create or update this CI workflow so that it:
# - Installs dependencies for the languages used in this repo.
# - Runs linting, tests, and schema validation (ajv-validate) where applicable.
# - Follows the principles in ../RZ-AI-Core-Standards/docs/LINTING_AND_CI_STANDARDS.md.
# Tailor steps to THIS repo's actual tooling (pytest, npm test, etc.).
```

## 8. Documentation & Standards Audit (`audit_docs.py`)

Bring README and docs in line with standards.

In `README.md`:

```text
# Copilot Instruction:
# Update this README to:
# - Briefly describe how AI/LLMs are used in this project.
# - Point to config/prompts.yaml and config/models.yaml as the configuration locations.
# - Link to the relevant docs under docs/ (AI prompting standards, structure, data layout).
# Use ../RZ-AI-Core-Standards/docs/AI_PROJECT_REVIEW_CHECKLIST.md as a guide for what
# should be documented, but keep it specific to THIS repo.
```

In `docs/AI_PROMPTING_STANDARDS.md` (project-local):

```text
# Copilot Instruction:
# Create a project-specific AI prompting standards document for THIS repo using
# ../RZ-AI-Core-Standards/docs/AI_PROMPTING_STANDARDS.md as a template.
# - Document where prompts live (config/prompts.yaml).
# - Document how developers should add/modify prompts.
# - Document how prompts are wired into the LLM client(s).
# Omit sections that do not apply to this project.
```

In `docs/COPILOT_USAGE.md` (project-local):

```text
# Copilot Instruction:
# Based on ../RZ-AI-Core-Standards/docs/COPILOT_USAGE.md, generate a concise
# Copilot usage guide for THIS repo that:
# - Highlights common Copilot use cases here (e.g., test generation, pipeline refactoring).
# - Includes 2–3 concrete instruction blocks relevant to this codebase.
# - Excludes generic or unused patterns.
```

## 9. Master Health Check (`rz_ai_check.py` or equivalent)

When running a consolidated health check, you can drive remediation with a summary doc:

```text
# Copilot Instruction:
# The script rz_ai_check.py reports the following failing categories for THIS repo:
# {paste summary}
#
# For each failing category:
# - List the concrete files and changes that are likely needed.
# - Reference the relevant core docs from ../RZ-AI-Core-Standards/docs/.
# - Produce an ordered remediation plan (steps) that can be applied incrementally.
```

Use that plan as a checklist and apply the specific instruction blocks above, one category at a time.
