# AI Prompting Standards

All prompts must be:

- Stored in `config/prompts.yaml` (or a project-specific equivalent).
- Versioned via git (no ad-hoc prompt strings hidden in code).
- Designed using the same structure:

**Prompt structure:**

1. Role
1. Objective
1. Constraints
1. Procedure
1. Output format
1. Optional examples

## Example schema in `config/prompts.yaml`

```yaml
summarization:
  system: |
    You are a senior technical summarizer. Be concise and accurate.
  user_template: |
    Summarize the following text into {n_sentences} sentences:
    ---
    {text}

code_debug:
  system: |
    You are a senior Python engineer. Fix bugs with minimal changes.
  user_template: |
    Here is the error:

    {error}

    Here is the relevant code:

    {code}

    Provide:
    1. Root cause
    2. Minimal fix
    3. Corrected code block
```

Rules

- Do not hard-code long prompts inside `.py`, `.ts`, `.cpp` files.
- Every production LLM call must reference a named prompt in `config/prompts.yaml`.
- Prompt versions must be tracked via standard git history (no silent edits).
