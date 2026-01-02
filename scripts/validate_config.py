#!/usr/bin/env python3
"""Validate template config YAML files using JSON Schema and Pydantic."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping, Tuple, Type, cast

import yaml
from jsonschema import Draft202012Validator
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    PositiveInt,
    RootModel,
    field_validator,
    model_validator,
)
from pydantic import (
    ValidationError as PydanticValidationError,
)

ModelType = Type[BaseModel]
REPO_ROOT = Path(__file__).resolve().parents[1]

# ---------------------------------------------------------------------------
# Pydantic models provide an ergonomic, type-safe view of each config file.
# ---------------------------------------------------------------------------


class ModelConfig(BaseModel):
    """Validated model parameters for a specific provider/model pair."""

    model_config = ConfigDict(extra="forbid")

    provider: str
    model: str
    temperature: float = Field(ge=0.0, le=2.0)
    max_tokens: PositiveInt


class ProviderConfig(BaseModel):
    """Provider-level defaults and optional model allow-lists."""

    model_config = ConfigDict(extra="forbid")

    default_model: str
    coding_models: list[str] | None = None
    general_models: list[str] | None = None


class ModelsConfig(BaseModel):
    """Top-level models.yaml structure."""

    model_config = ConfigDict(extra="forbid")

    default: ModelConfig
    providers: Dict[str, ProviderConfig]


class PromptTemplate(BaseModel):
    """A single prompt template definition."""

    model_config = ConfigDict(extra="forbid")

    description: str = Field(min_length=1)
    system: str = Field(min_length=1)
    user_template: str = Field(min_length=1)
    output_format: str | None = None


class PromptsConfig(RootModel[Dict[str, PromptTemplate]]):
    """Mapping of prompt IDs to their templates."""


class DataPolicy(BaseModel):
    """Data handling policy metadata for a project."""

    model_config = ConfigDict(extra="forbid")

    pii: bool | None = None
    prod_data: bool | None = None
    data_classification: str | None = Field(
        None, pattern="^(public|internal|confidential|restricted)$"
    )
    retention_days: int | None = Field(None, ge=0)


class RepositoryInfo(BaseModel):
    """Repository metadata for the project config."""

    model_config = ConfigDict(extra="forbid")

    url: str | None = None
    branch: str = "main"


class ProjectConfig(BaseModel):
    """Top-level project.yaml structure."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1)
    description: str = Field(min_length=1)
    owner: str | list[str] | None = None
    languages: list[str] = Field(min_length=1)
    runtime: str = Field(pattern="^(batch|service|cli|notebook|library|hybrid)$")
    stack: list[str] | None = None
    data_policy: DataPolicy | None = None
    repository: RepositoryInfo | None = None
    version: str | None = Field(None, pattern=r"^\d+\.\d+\.\d+(-[a-zA-Z0-9]+)?$")
    status: str = Field("active", pattern="^(active|maintenance|deprecated|archived)$")


class EvalDataset(BaseModel):
    """Dataset locator and sampling options for an evaluation."""

    model_config = ConfigDict(extra="forbid")

    dataset_id: str | None = Field(None, min_length=1)
    data_path: str | None = Field(None, min_length=1)
    split: str | None = Field(None, min_length=1)
    max_samples: int | None = Field(None, ge=1)
    seed: int | None = Field(None, ge=0)

    @property
    def has_source(self) -> bool:
        """Return True if dataset_id or data_path is provided."""
        return bool(self.dataset_id) or bool(self.data_path)


class Evaluation(BaseModel):
    """A single evaluation definition within evals.yaml."""

    model_config = ConfigDict(extra="allow")

    id: str = Field(min_length=1)
    description: str = Field(min_length=1)
    dataset: EvalDataset
    prompt_id: str | list[str]
    models: list[str]
    metrics: list[str]
    thresholds: Dict[str, float] | None = None
    batch_size: int | None = Field(None, ge=1)
    parallelism: int | None = Field(None, ge=1)
    tags: list[str] | None = None

    @field_validator("models", "metrics")
    @classmethod
    def ensure_non_empty_list(cls, value: list[str]) -> list[str]:
        """Validate that list fields are non-empty.

        Args:
            value: List value to validate.

        Returns:
            The validated list.
        """
        if not value:
            raise ValueError("must contain at least one item")
        return value

    @field_validator("prompt_id")
    @classmethod
    def ensure_prompt_id(cls, value: str | list[str]) -> str | list[str]:
        """Validate that prompt_id is a non-empty string or list of strings.

        Args:
            value: Prompt id value to validate.

        Returns:
            The validated prompt id value.
        """
        if isinstance(value, str):
            if not value:
                raise ValueError("prompt_id cannot be empty")
        else:
            if not value:
                raise ValueError("prompt_id list cannot be empty")
            if any(not item for item in value):
                raise ValueError("prompt_id entries must be non-empty strings")
        return value

    @model_validator(mode="after")
    def ensure_dataset_source(self) -> "Evaluation":
        """Validate that the dataset includes dataset_id or data_path.

        Returns:
            The validated Evaluation instance.
        """
        if not self.dataset.has_source:
            raise ValueError("dataset must include dataset_id or data_path")
        return self


class EvalsConfig(BaseModel):
    """Top-level evals.yaml structure."""

    model_config = ConfigDict(extra="forbid")

    version: str | None = Field(None, min_length=1)
    evals: list[Evaluation]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def read_file_text(path: Path) -> str:
    """Read text from *path* with helpful error messages.

    Args:
        path: File path to read.

    Returns:
        File contents as text.
    """
    return path.read_text(encoding="utf-8")


def load_yaml(path: Path) -> Dict[str, Any]:
    """Load YAML from *path* and normalize keys to strings.

    Args:
        path: YAML file path.

    Returns:
        Parsed YAML mapping with keys normalized to strings.
    """
    data = yaml.safe_load(read_file_text(path))
    if data is None:
        return {}
    if not isinstance(data, Mapping):
        raise ValueError(f"YAML root must be a mapping: {path}")
    mapping_data = cast(Mapping[str, Any], data)
    result: Dict[str, Any] = {}
    for key, value in mapping_data.items():
        result[str(key)] = value
    return result


def load_schema(path: Path) -> Dict[str, Any]:
    """Load a JSON schema from *path*.

    Args:
        path: JSON schema file path.

    Returns:
        Parsed JSON schema mapping.
    """
    return cast(Dict[str, Any], json.loads(read_file_text(path)))


def jsonschema_errors(schema: Mapping[str, Any], data: Mapping[str, Any]) -> Iterable[str]:
    """Yield human-readable JSON Schema validation errors.

    Args:
        schema: JSON schema mapping.
        data: Data mapping to validate.

    Yields:
        Human-readable validation error strings.
    """
    validator: Any = Draft202012Validator(schema)
    for error in validator.iter_errors(data):
        location = "/".join(str(part) for part in error.path) or "<root>"
        yield f"{location}: {error.message}"


@dataclass
class ValidationResult:
    """Outcome of validating a single config document against schema and model."""

    label: str
    data_path: Path
    schema_path: Path
    ok: bool
    errors: list[str]


def validate_document(
    label: str,
    data_path: Path,
    schema_path: Path,
    model_class: ModelType,
) -> ValidationResult:
    """Validate one YAML config against both JSON Schema and a Pydantic model.

    Args:
        label: Document label used in output.
        data_path: YAML config file path.
        schema_path: JSON schema file path.
        model_class: Pydantic model class used for validation.

    Returns:
        ValidationResult describing success/failure and errors.
    """
    errors: list[str] = []
    try:
        data = load_yaml(data_path)
    except Exception as exc:  # noqa: BLE001
        return ValidationResult(label, data_path, schema_path, False, [f"YAML error: {exc}"])

    try:
        schema = load_schema(schema_path)
    except Exception as exc:  # noqa: BLE001
        return ValidationResult(label, data_path, schema_path, False, [f"Schema load error: {exc}"])

    schema_issues = list(jsonschema_errors(schema, data))
    errors.extend(f"Schema: {issue}" for issue in schema_issues)

    try:
        model_class.model_validate(data)
    except PydanticValidationError as exc:
        errors.append(f"Pydantic: {exc}")

    return ValidationResult(label, data_path, schema_path, ok=not errors, errors=errors)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments for validating config YAML files.

    Returns:
        Parsed CLI arguments.
    """
    parser = argparse.ArgumentParser(
        prog="validate_config",
        description=(
            "Validate config YAML files against JSON Schema and Pydantic models. "
            "Defaults to repo_root/config/*.yaml if present, otherwise "
            "repo_root/templates/config/*.yaml."
        ),
    )
    parser.add_argument(
        "--models",
        type=Path,
        default=None,
        help=(
            "Path to models.yaml (default: repo_root/config/models.yaml if present; "
            "otherwise repo_root/templates/config/models.yaml)"
        ),
    )
    parser.add_argument(
        "--models-schema",
        type=Path,
        default=None,
        help="Path to models JSON schema (default: repo_root/schemas/models.schema.json)",
    )
    parser.add_argument(
        "--prompts",
        type=Path,
        default=None,
        help=(
            "Path to prompts.yaml (default: repo_root/config/prompts.yaml if present; "
            "otherwise repo_root/templates/config/prompts.yaml)"
        ),
    )
    parser.add_argument(
        "--prompts-schema",
        type=Path,
        default=None,
        help="Path to prompts JSON schema (default: repo_root/schemas/prompts.schema.json)",
    )
    parser.add_argument(
        "--project",
        type=Path,
        default=None,
        help=(
            "Path to project.yaml (default: repo_root/config/project.yaml if present; "
            "otherwise repo_root/templates/config/project.yaml)"
        ),
    )
    parser.add_argument(
        "--project-schema",
        type=Path,
        default=None,
        help="Path to project JSON schema (default: repo_root/schemas/project_config.schema.json)",
    )
    parser.add_argument(
        "--evals",
        type=Path,
        default=None,
        help=(
            "Path to evals.yaml (default: repo_root/config/evals.yaml if present; "
            "otherwise repo_root/templates/config/evals.yaml)"
        ),
    )
    parser.add_argument(
        "--evals-schema",
        type=Path,
        default=None,
        help="Path to evals JSON schema (default: repo_root/schemas/eval_config.schema.json)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit JSON report instead of human-readable output",
    )
    return parser.parse_args()


def _resolve_paths(
    args: argparse.Namespace,
) -> Tuple[Path, Path, Path, Path, Path, Path, Path, Path]:
    config_dir = REPO_ROOT / "config"
    config_root = config_dir if config_dir.exists() else (REPO_ROOT / "templates/config")

    models_path = (args.models or (config_root / "models.yaml")).resolve()
    models_schema = (args.models_schema or (REPO_ROOT / "schemas/models.schema.json")).resolve()
    prompts_path = (args.prompts or (config_root / "prompts.yaml")).resolve()
    prompts_schema = (args.prompts_schema or (REPO_ROOT / "schemas/prompts.schema.json")).resolve()
    project_path = (args.project or (config_root / "project.yaml")).resolve()
    project_schema = (
        args.project_schema or (REPO_ROOT / "schemas/project_config.schema.json")
    ).resolve()
    evals_path = (args.evals or (config_root / "evals.yaml")).resolve()
    evals_schema = (args.evals_schema or (REPO_ROOT / "schemas/eval_config.schema.json")).resolve()
    return (
        models_path,
        models_schema,
        prompts_path,
        prompts_schema,
        project_path,
        project_schema,
        evals_path,
        evals_schema,
    )


def _render_json(results: list[ValidationResult]) -> None:
    payload: dict[str, Any] = {
        "results": [
            {
                "label": res.label,
                "data_path": str(res.data_path),
                "schema_path": str(res.schema_path),
                "ok": res.ok,
                "errors": res.errors,
            }
            for res in results
        ],
        "ok": all(res.ok for res in results),
    }
    print(json.dumps(payload, indent=2))


def _render_human(results: list[ValidationResult]) -> None:
    for res in results:
        if res.ok:
            print(f"OK {res.label} config valid: {res.data_path}")
        else:
            print(f"ERROR {res.label} invalid: {res.data_path}")
            for issue in res.errors:
                print(f"  - {issue}")


def main() -> None:
    """Validate config YAML files and exit non-zero if any fail."""
    args = parse_args()
    (
        models_path,
        models_schema,
        prompts_path,
        prompts_schema,
        project_path,
        project_schema,
        evals_path,
        evals_schema,
    ) = _resolve_paths(args)

    validations: Tuple[Tuple[str, Path, Path, ModelType], ...] = (
        ("models", models_path, models_schema, ModelsConfig),
        ("prompts", prompts_path, prompts_schema, PromptsConfig),
        ("project", project_path, project_schema, ProjectConfig),
        ("evals", evals_path, evals_schema, EvalsConfig),
    )

    results = [
        validate_document(label, data_path, schema_path, model_class)
        for label, data_path, schema_path, model_class in validations
    ]

    if args.json:
        _render_json(results)
    else:
        _render_human(results)

    if not all(res.ok for res in results):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
