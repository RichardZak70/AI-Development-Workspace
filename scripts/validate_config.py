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
from pydantic import BaseModel, ConfigDict, Field, PositiveInt, RootModel, ValidationError as PydanticValidationError

ModelType = Type[BaseModel]
REPO_ROOT = Path(__file__).resolve().parents[1]

# ---------------------------------------------------------------------------
# Pydantic models provide an ergonomic, type-safe view of each config file.
# ---------------------------------------------------------------------------


class ModelConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    provider: str
    model: str
    temperature: float = Field(ge=0.0, le=2.0)
    max_tokens: PositiveInt


class ProviderConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    default_model: str
    coding_models: list[str] | None = None
    general_models: list[str] | None = None


class ModelsConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    default: ModelConfig
    providers: Dict[str, ProviderConfig]


class PromptTemplate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    description: str | None = None
    system: str = Field(min_length=1)
    user_template: str = Field(min_length=1)
    output_format: str | None = None


class PromptsConfig(RootModel[Dict[str, PromptTemplate]]):
    """Mapping of prompt IDs to their templates."""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def read_file_text(path: Path) -> str:
    """Read text from *path* with helpful error messages."""

    return path.read_text(encoding="utf-8")


def load_yaml(path: Path) -> Dict[str, Any]:
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
    return cast(Dict[str, Any], json.loads(read_file_text(path)))


def jsonschema_errors(schema: Mapping[str, Any], data: Mapping[str, Any]) -> Iterable[str]:
    validator: Any = Draft202012Validator(schema)
    for error in validator.iter_errors(data):
        location = "/".join(str(part) for part in error.path) or "<root>"
        yield f"{location}: {error.message}"


@dataclass
class ValidationResult:
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
    parser = argparse.ArgumentParser(
        description="Validate template configs against JSON Schema and Pydantic models"
    )
    parser.add_argument(
        "--models",
        type=Path,
        default=None,
        help="Path to models.yaml (default: repo_root/templates/config/models.yaml)",
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
        help="Path to prompts.yaml (default: repo_root/templates/config/prompts.yaml)",
    )
    parser.add_argument(
        "--prompts-schema",
        type=Path,
        default=None,
        help="Path to prompts JSON schema (default: repo_root/schemas/prompts.schema.json)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit JSON report instead of human-readable output",
    )
    return parser.parse_args()


def main() -> None:  # noqa: C901
    args = parse_args()
    models_path = (args.models or (REPO_ROOT / "templates/config/models.yaml")).resolve()
    models_schema = (args.models_schema or (REPO_ROOT / "schemas/models.schema.json")).resolve()
    prompts_path = (args.prompts or (REPO_ROOT / "templates/config/prompts.yaml")).resolve()
    prompts_schema = (args.prompts_schema or (REPO_ROOT / "schemas/prompts.schema.json")).resolve()

    validations: Tuple[Tuple[str, Path, Path, ModelType], ...] = (
        ("models", models_path, models_schema, ModelsConfig),
        ("prompts", prompts_path, prompts_schema, PromptsConfig),
    )

    results = [validate_document(label, data_path, schema_path, model_class) for label, data_path, schema_path, model_class in validations]

    if args.json:
        payload = {
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
    else:
        for res in results:
            if res.ok:
                print(f"✅ {res.label} config valid: {res.data_path}")
            else:
                print(f"❌ {res.label} invalid: {res.data_path}")
                for issue in res.errors:
                    print(f"  - {issue}")

    if not all(res.ok for res in results):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
