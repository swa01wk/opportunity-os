"""T-33 contract codegen, drift and equivalence (SPEC-03a)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from fixture_harness import pydantic_validator, register_schema, validate_with_pydantic
from jsonschema import Draft202012Validator, RefResolver
from schema_compare import schema_diff

from opportunityos_contracts._build import generate
from opportunityos_contracts.events.workflow_request import WorkflowRequest

REPO_ROOT = Path(__file__).resolve().parents[2]
BASELINES = Path(__file__).resolve().parent / "baselines"
COMMON_SCHEMA = REPO_ROOT / "docs" / "contracts" / "common.schema.json"
WORKFLOW_SCHEMA = REPO_ROOT / "docs" / "contracts" / "events" / "workflow-request.schema.json"
PREVIEW_FIXTURE = REPO_ROOT / "docs" / "contracts" / "examples" / "preview.workflow-request.json"
GENERATED_PATHS = (
    COMMON_SCHEMA,
    WORKFLOW_SCHEMA,
    REPO_ROOT / "contracts/ts/src/index.ts",
)

register_schema("events/workflow-request.schema.json", pydantic_validator(WorkflowRequest))


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _snapshot_generated() -> dict[Path, bytes]:
    return {path: path.read_bytes() for path in GENERATED_PATHS}


@pytest.mark.t("T-33")
def test_contracts_is_idempotent() -> None:
    generate()
    before = _snapshot_generated()
    generate()
    after = _snapshot_generated()
    assert before == after


@pytest.mark.t("T-33")
def test_regeneration_replaces_a_hand_edit() -> None:
    generate()
    canonical = COMMON_SCHEMA.read_text(encoding="utf-8")
    COMMON_SCHEMA.write_text(canonical.replace("0.1.0", "0.1.1"), encoding="utf-8")
    assert COMMON_SCHEMA.read_text(encoding="utf-8") != canonical
    generate()
    assert COMMON_SCHEMA.read_text(encoding="utf-8") == canonical


@pytest.mark.t("T-33")
def test_common_schema_matches_stage_2a_baseline() -> None:
    expected = _load_json(BASELINES / "common.stage2a.json")
    actual = _load_json(COMMON_SCHEMA)
    diff = schema_diff(expected, actual)
    assert not diff, "\n".join(diff[:20])


@pytest.mark.t("T-33")
def test_workflow_schema_matches_040_except_diagnostic() -> None:
    expected = _load_json(BASELINES / "workflow-request.0.4.0.json")
    actual = _load_json(WORKFLOW_SCHEMA)
    expected_types = list(expected["properties"]["workflowType"]["enum"])
    actual_types = list(actual["properties"]["workflowType"]["enum"])
    assert actual_types == [*expected_types, "diagnostic"]
    expected["properties"]["workflowType"]["enum"] = actual_types
    diff = schema_diff(expected, actual)
    assert not diff, "\n".join(diff[:20])


@pytest.mark.t("T-33")
def test_preview_fixture_validates_in_pydantic() -> None:
    payload = json.loads(PREVIEW_FIXTURE.read_text(encoding="utf-8"))
    assert validate_with_pydantic("events/workflow-request.schema.json", payload)


@pytest.mark.t("T-33")
def test_preview_fixture_validates_in_json_schema() -> None:
    workflow = _load_json(WORKFLOW_SCHEMA)
    common = _load_json(COMMON_SCHEMA)
    base = WORKFLOW_SCHEMA.parent.as_uri() + "/"
    resolver = RefResolver(base, workflow, store={f"{base}../common.schema.json": common})
    validator = Draft202012Validator(workflow, resolver=resolver)
    payload = json.loads(PREVIEW_FIXTURE.read_text(encoding="utf-8"))
    validator.validate(payload)
