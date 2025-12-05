#!/usr/bin/env python3
"""Validate template config YAML files using JSON Schema and Pydantic."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, Iterable, Tuple, Type

import yaml
from jsonschema import Draft202012Validator
from pydantic import BaseModel, Field, PositiveInt, RootModel, ValidationError as PydanticValidationError

ModelType = Type[BaseModel]

# ---------------------------------------------------------------------------
# Pydantic models provide an ergonomic, type-safe view of each config file.
# ---------------------------------------------------------------------------


class ModelConfig(BaseModel):
    provider: str
    model: str
    temperature: float = Field(ge=0.0, le=2.0)
    max_tokens: PositiveInt


class ProviderConfig(BaseModel):
    default_model: str


class ModelsConfig(BaseModel):
    default: ModelConfig
    providers: Dict[str, ProviderConfig]


class PromptTemplate(BaseModel):
    system: str
    user_template: str


class PromptsConfig(RootModel[Dict[str, PromptTemplate]]):
    """Mapping of prompt IDs to their templates."""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def read_file_text(path: Path) -> str:
    """Read text from *path* with helpful error messages."""

    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"File not found: {path}") from exc


def load_yaml(path: Path) -> Dict[str, Any]:
    data = yaml.safe_load(read_file_text(path))
    return data or {}


def load_schema(path: Path) -> Dict[str, Any]:
    return json.loads(read_file_text(path))


def jsonschema_errors(schema: Dict[str, Any], data: Dict[str, Any]) -> Iterable[str]:
    validator = Draft202012Validator(schema)
    for error in validator.iter_errors(data):
        location = "/".join(str(part) for part in error.path) or "<root>"
        yield f"{location}: {error.message}"


def validate_document(
    label: str,
    data_path: Path,
    schema_path: Path,
    model_class: ModelType,
) -> None:
    data = load_yaml(data_path)
    schema = load_schema(schema_path)

    issues = list(jsonschema_errors(schema, data))
    if issues:
        joined = "\n  - ".join(issues)
        raise SystemExit(
            f"Schema validation failed for {label} ({data_path}):\n  - {joined}"
        )

    try:
        model_class.model_validate(data)
    except PydanticValidationError as exc:
        raise SystemExit(
            f"Pydantic validation failed for {label} ({data_path}):\n{exc}"
        ) from exc

    print(f"✅ {label} config valid: {data_path}")


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
        default=Path("templates/config/models.yaml"),
        help="Path to models.yaml",
    )
    parser.add_argument(
        "--models-schema",
        type=Path,
        default=Path("schemas/models.schema.json"),
        help="Path to models JSON schema",
    )
    parser.add_argument(
        "--prompts",
        type=Path,
        default=Path("templates/config/prompts.yaml"),
        help="Path to prompts.yaml",
    )
    parser.add_argument(
        "--prompts-schema",
        type=Path,
        default=Path("schemas/prompts.schema.json"),
        help="Path to prompts JSON schema",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    validations: Tuple[Tuple[str, Path, Path, ModelType], ...] = (
        ("models", args.models, args.models_schema, ModelsConfig),
        ("prompts", args.prompts, args.prompts_schema, PromptsConfig),
    )

    for label, data_path, schema_path, model_class in validations:
        validate_document(label, data_path, schema_path, model_class)


if __name__ == "__main__":
    main()
