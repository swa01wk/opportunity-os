"""Dual-runtime fixture registry for contract schemas (SPEC-03a)."""

from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any

from fixture_catalog import REPO_ROOT, FixtureCase, load_fixture_cases
from jsonschema import Draft202012Validator, RefResolver
from jsonschema.exceptions import ValidationError as JsonSchemaValidationError
from pydantic import BaseModel, ValidationError

Validator = Callable[[dict[str, Any]], None]

CONTRACTS_DIR = REPO_ROOT / "docs" / "contracts"
COMMON_SCHEMA_PATH = CONTRACTS_DIR / "common.schema.json"
WORKFLOW_SCHEMA_PATH = CONTRACTS_DIR / "events/workflow-request.schema.json"

REGISTERED: dict[str, Validator] = {}
REGISTERED_JSON: dict[str, Validator] = {}


def pydantic_validator(model: type[BaseModel]) -> Validator:
    def _validate(payload: dict[str, Any]) -> None:
        model.model_validate(payload)

    return _validate


def _workflow_json_schema_validator() -> Validator:
    common = json.loads(COMMON_SCHEMA_PATH.read_text(encoding="utf-8"))
    workflow = json.loads(WORKFLOW_SCHEMA_PATH.read_text(encoding="utf-8"))
    base = WORKFLOW_SCHEMA_PATH.parent.as_uri() + "/"
    resolver = RefResolver(
        base_uri=base,
        referrer=workflow,
        store={f"{base}../common.schema.json": common},
    )
    validator = Draft202012Validator(workflow, resolver=resolver)

    def _validate(payload: dict[str, Any]) -> None:
        validator.validate(payload)

    return _validate


def register_schema(contract_path: str, *, pydantic: Validator) -> None:
    if contract_path == "events/workflow-request.schema.json":
        json_schema = _workflow_json_schema_validator()
    else:
        msg = f"no json schema validator for {contract_path}"
        raise ValueError(msg)
    REGISTERED[contract_path] = pydantic
    REGISTERED_JSON[contract_path] = json_schema


def validate_pydantic(contract_path: str, payload: dict[str, Any]) -> bool:
    try:
        REGISTERED[contract_path](payload)
        return True
    except ValidationError:
        return False


def validate_json_schema(contract_path: str, payload: dict[str, Any]) -> bool:
    try:
        REGISTERED_JSON[contract_path](payload)
        return True
    except JsonSchemaValidationError:
        return False


def load_fixture_payload(case: FixtureCase) -> dict[str, Any]:
    path = REPO_ROOT / "docs/contracts/examples" / case.file
    return json.loads(path.read_text(encoding="utf-8"))


def all_fixture_cases() -> list[FixtureCase]:
    return load_fixture_cases()
