"""Dual-runtime fixture registry for contract schemas (SPEC-03a)."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel, ValidationError

Validator = Callable[[dict[str, Any]], None]


@dataclass(frozen=True)
class RegisteredSchema:
    contract_path: str
    validate: Validator


REGISTERED: dict[str, RegisteredSchema] = {}


def register_schema(contract_path: str, validate: Validator) -> None:
    REGISTERED[contract_path] = RegisteredSchema(contract_path=contract_path, validate=validate)


def pydantic_validator(model: type[BaseModel]) -> Validator:
    def _validate(payload: dict[str, Any]) -> None:
        model.model_validate(payload)

    return _validate


def validate_with_pydantic(contract_path: str, payload: dict[str, Any]) -> bool:
    registration = REGISTERED[contract_path]
    try:
        registration.validate(payload)
        return True
    except ValidationError:
        return False
