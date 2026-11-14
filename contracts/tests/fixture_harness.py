"""Dual-runtime fixture registry for contract schemas (SPEC-03a)."""

from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any

from fixture_catalog import REPO_ROOT, FixtureCase, load_fixture_cases
from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError as JsonSchemaValidationError
from pydantic import BaseModel, ValidationError
from referencing import Registry, Resource

Validator = Callable[[dict[str, Any]], None]

CONTRACTS_DIR = REPO_ROOT / "docs" / "contracts"

REGISTERED: dict[str, Validator] = {}
REGISTERED_JSON: dict[str, Validator] = {}

_SCHEMAS_BY_CONTRACT: dict[str, dict[str, Any]] = {}
_REGISTRY: Registry | None = None


def _build_schema_registry() -> Registry:
    global _REGISTRY, _SCHEMAS_BY_CONTRACT
    if _REGISTRY is not None:
        return _REGISTRY

    resources: list[tuple[str, Resource]] = []
    for path in sorted(CONTRACTS_DIR.rglob("*.schema.json")):
        rel = path.relative_to(CONTRACTS_DIR).as_posix()
        doc = json.loads(path.read_text(encoding="utf-8"))
        _SCHEMAS_BY_CONTRACT[rel] = doc
        schema_id = doc.get("$id")
        if isinstance(schema_id, str):
            resources.append((schema_id, Resource.from_contents(doc)))

    _REGISTRY = Registry().with_resources(tuple(resources))
    return _REGISTRY


def pydantic_validator(model: type[BaseModel]) -> Validator:
    def _validate(payload: dict[str, Any]) -> None:
        model.model_validate(payload)

    return _validate


def _json_schema_validator(contract_path: str) -> Validator:
    registry = _build_schema_registry()
    try:
        schema = _SCHEMAS_BY_CONTRACT[contract_path]
    except KeyError as exc:
        msg = f"no schema file for contract {contract_path}"
        raise ValueError(msg) from exc
    validator = Draft202012Validator(schema, registry=registry)

    def _validate(payload: dict[str, Any]) -> None:
        validator.validate(payload)

    return _validate


def register_schema(contract_path: str, *, pydantic: Validator) -> None:
    _build_schema_registry()
    if contract_path not in _SCHEMAS_BY_CONTRACT:
        msg = f"unknown contract {contract_path}"
        raise ValueError(msg)
    REGISTERED[contract_path] = pydantic
    REGISTERED_JSON[contract_path] = _json_schema_validator(contract_path)


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
