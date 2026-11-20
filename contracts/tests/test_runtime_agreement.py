"""T-33 pydantic vs jsonschema agreement on field mutations (SPEC-03b B4)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from fixture_catalog import load_fixture_cases
from fixture_harness import (
    _build_schema_registry,
    load_fixture_payload,
    register_schema,
    validate_json_schema,
    validate_pydantic,
)
from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError as JsonSchemaValidationError
from pydantic import BaseModel, ValidationError

from opportunityos_contracts.agent_tools.execution import AgentResult, TaskContract
from opportunityos_contracts.agent_tools.task_io import DiagnosticEchoInput, DiagnosticEchoOutput
from opportunityos_contracts.analytics.events import AnalyticsEvent
from opportunityos_contracts.events.domain_event import DomainEvent
from opportunityos_contracts.events.workflow_request import WorkflowRequest

EXECUTION_SCHEMA_ID = "https://opportunityos.invalid/contracts/agent-tools/execution.schema.json"
TASK_IO_SCHEMA_ID = "https://opportunityos.invalid/contracts/agent-tools/task-io.schema.json"

AGENT_VALID_EXAMPLES: tuple[tuple[str, object, str], ...] = (
    ("TaskContract", TaskContract, "task-contract.research.json"),
    ("AgentResult", AgentResult, "agent-result.failed.json"),
    ("DiagnosticEchoInput", DiagnosticEchoInput, "diagnostic-echo.input.json"),
    ("DiagnosticEchoOutput", DiagnosticEchoOutput, "diagnostic-echo.output.json"),
)

REPO_ROOT = Path(__file__).resolve().parents[2]

PROBE_KEY = "__runtime_agreement_probe__"

MUTATIONS: tuple[tuple[str, Any | object], ...] = (
    ("null", None),
    ("true", True),
    ("7", 7),
    ("1.0", 1.0),
    ("1.5", 1.5),
    ("x", "x"),
    ("1.5_str", "1.5"),
    ("{}", {}),
    ("[]", []),
)

register_schema(
    "events/workflow-request.schema.json",
    pydantic=lambda p: WorkflowRequest.model_validate(p),
)
register_schema(
    "events/domain-event.schema.json",
    pydantic=lambda p: DomainEvent.model_validate(p),
)
register_schema(
    "analytics/events.schema.json",
    pydantic=lambda p: AnalyticsEvent.model_validate(p),
)


def _clone(value: Any) -> Any:
    return json.loads(json.dumps(value))


def _path_str(parts: tuple[str | int, ...]) -> str:
    out = ""
    for part in parts:
        out += f"[{part}]" if isinstance(part, int) else (f".{part}" if out else str(part))
    return out or "$"


def _set_at(data: dict[str, Any], parts: tuple[str | int, ...], value: Any) -> None:
    cur: Any = data
    for part in parts[:-1]:
        cur = cur[part]
    cur[parts[-1]] = value


def _del_at(data: dict[str, Any], parts: tuple[str | int, ...]) -> None:
    cur: Any = data
    for part in parts[:-1]:
        cur = cur[part]
    del cur[parts[-1]]


def _iter_field_locations(
    value: Any,
    parts: tuple[str | int, ...] = (),
) -> list[tuple[tuple[str | int, ...], str | int]]:
    locations: list[tuple[tuple[str | int, ...], str | int]] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_parts = (*parts, key)
            locations.append((child_parts, key))
            locations.extend(_iter_field_locations(child, child_parts))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            child_parts = (*parts, index)
            locations.extend(_iter_field_locations(child, child_parts))
    return locations


def _iter_object_paths(
    value: Any,
    parts: tuple[str | int, ...] = (),
) -> list[tuple[str | int, ...]]:
    paths: list[tuple[str | int, ...]] = []
    if isinstance(value, dict):
        paths.append(parts)
        for key, child in value.items():
            paths.extend(_iter_object_paths(child, (*parts, key)))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            paths.extend(_iter_object_paths(child, (*parts, index)))
    return paths


def _node_at(data: Any, parts: tuple[str | int, ...]) -> Any:
    cur = data
    for part in parts:
        cur = cur[part]
    return cur


def _assert_same_verdict(
    contract: str,
    payload: dict[str, Any],
    *,
    example: str,
    detail: str,
) -> None:
    pydantic_ok = validate_pydantic(contract, payload)
    json_ok = validate_json_schema(contract, payload)
    assert pydantic_ok == json_ok, (
        f"{example}: {detail} — pydantic={pydantic_ok} jsonschema={json_ok}"
    )


def _load_example(name: str) -> dict[str, Any]:
    payload = json.loads((REPO_ROOT / "docs/contracts/examples" / name).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        msg = f"{name} is not a JSON object"
        raise TypeError(msg)
    return payload


def _def_validator(schema_id: str, def_name: str) -> Draft202012Validator:
    registry = _build_schema_registry()
    return Draft202012Validator(
        {"$ref": f"{schema_id}#/$defs/{def_name}"},
        registry=registry,
    )


def _json_schema_ok(schema_id: str, def_name: str, payload: dict[str, Any]) -> bool:
    try:
        _def_validator(schema_id, def_name).validate(payload)
        return True
    except JsonSchemaValidationError:
        return False


def _pydantic_ok(model: type[BaseModel], payload: dict[str, Any]) -> bool:
    try:
        model.model_validate(payload)
        return True
    except ValidationError:
        return False


def _assert_agent_verdict(
    *,
    schema_id: str,
    def_name: str,
    model: type[BaseModel],
    payload: dict[str, Any],
    example: str,
    detail: str,
) -> None:
    pydantic_ok = _pydantic_ok(model, payload)
    json_ok = _json_schema_ok(schema_id, def_name, payload)
    assert pydantic_ok == json_ok, (
        f"{example}: {detail} — pydantic={pydantic_ok} jsonschema={json_ok}"
    )


def _exercise_agent(
    *,
    schema_id: str,
    def_name: str,
    model: type[BaseModel],
    example: str,
    payload: dict[str, Any],
) -> None:
    for parts, _key in _iter_field_locations(payload):
        for label, mutation_value in MUTATIONS:
            mutated = _clone(payload)
            _set_at(mutated, parts, mutation_value)
            _assert_agent_verdict(
                schema_id=schema_id,
                def_name=def_name,
                model=model,
                payload=mutated,
                example=example,
                detail=f"set {_path_str(parts)} to {label}",
            )
        mutated = _clone(payload)
        _del_at(mutated, parts)
        _assert_agent_verdict(
            schema_id=schema_id,
            def_name=def_name,
            model=model,
            payload=mutated,
            example=example,
            detail=f"remove {_path_str(parts)}",
        )
    for obj_path in _iter_object_paths(payload):
        mutated = _clone(payload)
        node = _node_at(mutated, obj_path)
        assert isinstance(node, dict)
        node[PROBE_KEY] = True
        _assert_agent_verdict(
            schema_id=schema_id,
            def_name=def_name,
            model=model,
            payload=mutated,
            example=example,
            detail=f"extra property on object at {_path_str(obj_path) or '$'}",
        )


def _exercise_payload(contract: str, example: str, payload: dict[str, Any]) -> None:
    for parts, _key in _iter_field_locations(payload):
        for label, mutation_value in MUTATIONS:
            mutated = _clone(payload)
            _set_at(mutated, parts, mutation_value)
            _assert_same_verdict(
                contract,
                mutated,
                example=example,
                detail=f"set {_path_str(parts)} to {label}",
            )
        mutated = _clone(payload)
        _del_at(mutated, parts)
        _assert_same_verdict(
            contract,
            mutated,
            example=example,
            detail=f"remove {_path_str(parts)}",
        )
    for obj_path in _iter_object_paths(payload):
        mutated = _clone(payload)
        node = _node_at(mutated, obj_path)
        assert isinstance(node, dict)
        node[PROBE_KEY] = True
        _assert_same_verdict(
            contract,
            mutated,
            example=example,
            detail=f"extra property on object at {_path_str(obj_path) or '$'}",
        )


@pytest.mark.t("T-33")
def test_pydantic_and_json_schema_agree_on_field_mutations() -> None:
    valid = [case for case in load_fixture_cases() if case.expect_valid]
    assert valid, "expected at least one valid fixture per registered contract"
    for case in valid:
        payload = load_fixture_payload(case)
        assert isinstance(payload, dict)
        _exercise_payload(case.contract, case.file, payload)


_AGENT_SCHEMA_FOR: dict[type[BaseModel], tuple[str, str]] = {
    TaskContract: (EXECUTION_SCHEMA_ID, "TaskContract"),
    AgentResult: (EXECUTION_SCHEMA_ID, "AgentResult"),
    DiagnosticEchoInput: (TASK_IO_SCHEMA_ID, "DiagnosticEchoInput"),
    DiagnosticEchoOutput: (TASK_IO_SCHEMA_ID, "DiagnosticEchoOutput"),
}


@pytest.mark.t("T-33")
def test_agent_contract_models_agree_on_field_mutations() -> None:
    for def_name, model, file in AGENT_VALID_EXAMPLES:
        schema_id, json_def = _AGENT_SCHEMA_FOR[model]
        assert json_def == def_name
        payload = _load_example(file)
        _exercise_agent(
            schema_id=schema_id,
            def_name=json_def,
            model=model,
            example=file,
            payload=payload,
        )


@pytest.mark.t("T-33")
def test_agent_contract_models_reject_shared_invalid_cases() -> None:
    base_contract = _load_example("task-contract.research.json")
    base_result = _load_example("agent-result.failed.json")
    rejects: list[tuple[str, str, type[BaseModel], dict[str, Any]]] = [
        (
            EXECUTION_SCHEMA_ID,
            "TaskContract",
            TaskContract,
            {**base_contract, "outputDisposition": "attempt_only"},
        ),
        (
            EXECUTION_SCHEMA_ID,
            "TaskContract",
            TaskContract,
            {**base_contract, "reviewGate": "none"},
        ),
        (
            EXECUTION_SCHEMA_ID,
            "AgentResult",
            AgentResult,
            {**base_result, "proposedActions": [{"kind": "noop"}]},
        ),
        (TASK_IO_SCHEMA_ID, "DiagnosticEchoInput", DiagnosticEchoInput, {"text": ""}),
        (TASK_IO_SCHEMA_ID, "DiagnosticEchoInput", DiagnosticEchoInput, {"text": "x" * 201}),
    ]
    for schema_id, def_name, model, payload in rejects:
        assert not _pydantic_ok(model, payload)
        assert not _json_schema_ok(schema_id, def_name, payload)
