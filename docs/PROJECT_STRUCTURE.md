# RZ AI Project Structure Standard

Every AI-related project **must** follow this structure (or a compatible superset):

```text
project-root/
├── src/              # main source code (any language)
│   ├── config/       # runtime settings, env handling, schema definitions
│   ├── llm/          # LLM clients, prompt runners, wrappers
│   ├── pipelines/    # high-level workflows using LLMs
│   └── tools/        # shared helpers (logging, caching, error handling, etc.)
│
├── config/
│   ├── prompts.yaml  # prompt definitions by name
│   ├── models.yaml   # model and provider configuration
│   └── logging.yaml  # logging configuration (optional)
│
├── data/
│   ├── raw/          # immutable original data
│   ├── processed/    # cleaned / normalized data
│   ├── prompts/      # prompt experiments, AB tests, prompt logs
│   ├── outputs/      # model outputs, evaluations, artifacts
│   ├── cache/        # cached LLM responses, temporary files
│   └── embeddings/   # vector data and metadata
│
├── notebooks/
│   ├── 01_experiment_template.ipynb
│   └── 02_prompt_testing_template.ipynb
│
├── tests/            # automated tests (unit, integration, schema checks)
│
├── docs/             # project-specific docs; may link back to core standards
│
├── scripts/          # utility scripts (data prep, audits, migrations)
│
└── README.md
```

Any deviation must be justified in the project README.
