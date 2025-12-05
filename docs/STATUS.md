# AI Core Standards Project Status

This document tracks the status of the RZ AI Core Standards repository.

## 1. Repository Scaffolding

- [x] Initialize `AI-Core-Standards` repo and `main` branch.
- [x] Add root `README.md` describing purpose and layout.
- [x] Add `LICENSE` (MIT).
- [x] Create core folders: `docs/`, `templates/`, `scripts/`.

## 2. Core Documentation

- [x] `docs/PROJECT_STRUCTURE.md` – RZ AI Project Structure Standard.
- [x] `docs/AI_PROMPTING_STANDARDS.md` – prompt storage and structure rules.
- [x] `docs/COPILOT_USAGE.md` – Copilot usage standard and patterns.
- [x] `docs/DATA_ORGANIZATION.md` – data directories and traceability rules.
- [x] `docs/SCHEMAS_AND_VALIDATION.md` – schema and validation requirements.
- [x] `docs/LINTING_AND_CI_STANDARDS.md` – linting/CI expectations.
- [x] `docs/AI_PROJECT_REVIEW_CHECKLIST.md` – production readiness checklist.
- [x] `docs/STATUS.md` – status and roadmap.

## 3. Templates

- [x] `templates/config/prompts.yaml` – base `summarization` and `code_debug` prompts.
- [x] `templates/config/models.yaml` – default provider/model catalog.
- [x] `templates/data_layout.txt` – standard `data/` folder layout.
- [x] `templates/.editorconfig` – editor consistency rules.
- [x] `templates/.gitignore_ai_project` – ignore patterns for AI projects.

## 4. Tooling and Scripts

- [x] `scripts/audit_ai_project.py` – checks presence of required config/data/docs.
- [x] `scripts/migrate_prompts_from_code.py` – placeholder for future migration tool.
- [ ] Add tests for `audit_ai_project.py` in a sample project (optional).

## 5. Linting and Quality

- [x] Configure markdownlint for this repo (config file + npm dependency).
- [ ] Run markdownlint cleanly on all `.md` files.
- [ ] Add a simple CI workflow to enforce markdownlint on pull requests.

---

### How to run markdownlint locally (once configured)

From the repo root:

```powershell
npm install --save-dev markdownlint-cli
npx markdownlint-cli "docs/**/*.md"
```
