# Schemas and Validation

All AI projects must enforce schemas on:

- LLM outputs used by downstream systems.
- Any structured data ingested from external sources.

## Requirements

- Define a clear output schema (JSON schema, Pydantic model, TS interface, etc.).
- Validate LLM output against this schema before use.
- Reject or handle invalid outputs explicitly (no silent failures).

Example (Python / Pydantic):

```python
from pydantic import BaseModel


class Extraction(BaseModel):
    name: str | None
    email: str | None
    phone: str | None
```

Prompt must instruct the model to return a JSON object matching the schema.
Validation must run before data is stored or further processed.

## Config schemas (required)

Configuration files are also part of the system contract and must be schema-validated.

- `config/models.yaml`: model/provider configuration
- `config/prompts.yaml`: prompt definitions
- `config/evals.yaml`: evaluation definitions
- `config/project.yaml`: project metadata

### Documentation is data

For YAML config files, documentation must be captured in the file itself via required fields (not just `#` comments).

- Prompt entries in `config/prompts.yaml` must include a non-empty `description`.
- Eval entries in `config/evals.yaml` must include a non-empty `description`.
- `config/project.yaml` must include a non-empty `description`.

This ensures docs are machine-checkable and enforced consistently in CI.
