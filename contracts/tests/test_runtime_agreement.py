"""T-33 pydantic vs jsonschema agreement on field mutations (SPEC-03b B4)."""

from __future__ import annotations

import json
from typing import Any

import pytest
from fixture_catalog import load_fixture_cases
from fixture_harness import (
    load_fixture_payload,
    register_schema,
    validate_json_schema,
    validate_pydantic,
)

from opportunityos_contracts.analytics.events import AnalyticsEvent
from opportunityos_contracts.events.domain_event import DomainEvent
from opportunityos_contracts.events.workflow_request import WorkflowRequest

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
