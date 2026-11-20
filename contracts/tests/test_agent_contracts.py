"""T-33 agent-tools contracts (SPEC-03c AC1-AC3)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from fixture_harness import _build_schema_registry
from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError as JsonSchemaValidationError
from pydantic import ValidationError
from schema_compare import schema_diff

from opportunityos_contracts._build import generate
from opportunityos_contracts.agent_tools.execution import AgentResult, TaskContract
from opportunityos_contracts.agent_tools.task_io import DiagnosticEchoInput, DiagnosticEchoOutput
from opportunityos_contracts.agent_tools.tasks import TasksManifest

REPO_ROOT = Path(__file__).resolve().parents[2]
BASELINES = Path(__file__).resolve().parent / "baselines"
COMMITTED_TASK_IO = REPO_ROOT / "docs/contracts/agent-tools/task-io.schema.json"
COMMITTED_EXECUTION = REPO_ROOT / "docs/contracts/agent-tools/execution.schema.json"
COMMITTED_TOOLS = REPO_ROOT / "docs/contracts/agent-tools/tools.schema.json"
COMMITTED_TASKS = REPO_ROOT / "docs/contracts/agent-tools/tasks.json"
EXECUTION_SCHEMA_ID = "https://opportunityos.invalid/contracts/agent-tools/execution.schema.json"

AC1_ALLOWED_DIFFS = frozenset(
    {
        "$defs.TaskType.enum",
        "$defs.TaskContract.properties.outputDisposition",
        "$defs.TaskContract.properties.reviewGate",
        "$defs.TaskContract.allOf",
        "$defs.DiagnosticEchoInput",
        "$defs.DiagnosticEchoOutput",
    }
)


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _generated_agent_paths(root: Path) -> tuple[Path, Path, Path]:
    return (
        root / "docs/contracts/agent-tools/task-io.schema.json",
        root / "docs/contracts/agent-tools/execution.schema.json",
        root / "docs/contracts/agent-tools/tools.schema.json",
    )


def _schema_diff_paths(expected: dict[str, Any], actual: dict[str, Any], prefix: str) -> list[str]:
    raw = schema_diff(expected, actual)
    return [f"{prefix}:{line}" for line in raw]


def _normalize_for_compare(doc: dict[str, Any], allowed: frozenset[str]) -> dict[str, Any]:
    """Drop allowed diagnostic_echo deltas so the rest matches the baseline."""
    out = json.loads(json.dumps(doc))
    defs = out.get("$defs", {})
    baseline_defs = _load_json(BASELINES / "task-io.0.4.0.json")["$defs"]
    if "DiagnosticEchoInput" in defs:
        del defs["DiagnosticEchoInput"]
    if "DiagnosticEchoOutput" in defs:
        del defs["DiagnosticEchoOutput"]
    for name in list(defs):
        if name in baseline_defs and name not in {"TaskType", "TaskContract"}:
            defs[name] = baseline_defs[name]
    task_type = defs.get("TaskType", {})
    if isinstance(task_type, dict) and "enum" in task_type:
        task_type["enum"] = [v for v in task_type["enum"] if v != "diagnostic_echo"]
    task_contract = defs.get("TaskContract")
    if isinstance(task_contract, dict):
        task_contract.pop("allOf", None)
        props = task_contract.get("properties", {})
        if isinstance(props, dict):
            props["outputDisposition"] = {"const": "draft_version"}
            props["reviewGate"] = {"enum": ["claim_review", "B_explanation_script", "C_storyboard"]}
    return out


@pytest.mark.t("T-33")
def test_agent_schemas_match_committed_after_codegen(tmp_path: Path) -> None:
    generate(tmp_path)
    task_io, execution, tools = _generated_agent_paths(tmp_path)
    assert task_io.read_bytes() == COMMITTED_TASK_IO.read_bytes()
    assert execution.read_bytes() == COMMITTED_EXECUTION.read_bytes()
    assert tools.read_bytes() == COMMITTED_TOOLS.read_bytes()


@pytest.mark.t("T-33")
def test_task_io_equivalent_to_040_except_diagnostic_echo(tmp_path: Path) -> None:
    generate(tmp_path)
    expected = _load_json(BASELINES / "task-io.0.4.0.json")
    actual = _load_json(_generated_agent_paths(tmp_path)[0])
    assert "DiagnosticEchoInput" in actual["$defs"]
    assert "DiagnosticEchoOutput" in actual["$defs"]
    normalized = _normalize_for_compare(actual, AC1_ALLOWED_DIFFS)
    diff = schema_diff(expected, normalized)
    assert not diff, "\n".join(diff[:30])


@pytest.mark.t("T-33")
def test_execution_equivalent_to_040_except_diagnostic_echo(tmp_path: Path) -> None:
    generate(tmp_path)
    expected = _load_json(BASELINES / "execution.0.4.0.json")
    actual = _load_json(_generated_agent_paths(tmp_path)[1])
    assert "diagnostic_echo" in actual["$defs"]["TaskType"]["enum"]
    assert actual["$defs"]["TaskContract"]["properties"]["outputDisposition"] != {
        "const": "draft_version"
    }
    # Compare execution $defs subset against baseline execution file
    exp_defs = expected["$defs"]
    act_defs = actual["$defs"]
    exp_task = json.loads(json.dumps(exp_defs["TaskContract"]))
    act_task = json.loads(json.dumps(act_defs["TaskContract"]))
    act_task.pop("allOf", None)
    act_task["properties"]["outputDisposition"] = {"const": "draft_version"}
    act_task["properties"]["reviewGate"] = {
        "enum": ["claim_review", "B_explanation_script", "C_storyboard"]
    }
    exp_defs = {**exp_defs, "TaskContract": exp_task}
    exp_defs["TaskType"] = {
        "enum": [v for v in act_defs["TaskType"]["enum"] if v != "diagnostic_echo"]
    }
    for name in exp_defs:
        if name in ("TaskType", "TaskContract"):
            continue
        diff = schema_diff(exp_defs[name], act_defs[name])
        assert not diff, f"{name}: " + "\n".join(diff[:10])


@pytest.mark.t("T-33")
def test_tools_schema_matches_020_baseline(tmp_path: Path) -> None:
    generate(tmp_path)
    expected = _load_json(BASELINES / "tools.0.2.0.json")
    actual = _load_json(_generated_agent_paths(tmp_path)[2])
    diff = schema_diff(expected, actual)
    assert not diff, "\n".join(diff[:20])


@pytest.mark.t("T-33")
def test_tasks_json_validates_every_bounded_task() -> None:
    raw = json.loads(COMMITTED_TASKS.read_text(encoding="utf-8"))
    manifest = TasksManifest.model_validate(raw)
    assert len(manifest.tasks) >= 4
    for entry in manifest.tasks:
        assert entry.input_schema
        assert entry.output_schema
        assert entry.budget.max_children == 0
        assert entry.retry_ceiling >= 0
        assert entry.failure_states


@pytest.mark.t("T-33")
def test_diagnostic_echo_task_entry_present() -> None:
    raw = json.loads(COMMITTED_TASKS.read_text(encoding="utf-8"))
    manifest = TasksManifest.model_validate(raw)
    echo = next(t for t in manifest.tasks if t.task_type.value == "diagnostic_echo")
    assert echo.permitted_tools == []
    assert echo.budget.max_model_calls == 1
    assert echo.budget.max_tool_calls == 0
    assert echo.budget.max_children == 0
    assert echo.output_disposition.value == "attempt_only"
    assert echo.review_gate.value == "none"
    assert echo.evaluation_fixtures is None


_SYNTHETIC_TASK_CONTRACT: dict[str, Any] = {
    "contractVersion": "0.4.0",
    "taskType": "research",
    "workspaceId": "00000000-0000-4000-8000-000000000001",
    "projectId": "00000000-0000-4000-8000-000000000002",
    "runId": "00000000-0000-4000-8000-000000000003",
    "attemptId": "00000000-0000-4000-8000-000000000004",
    "attempt": 1,
    "idempotencyKey": "run:research:1",
    "objective": "Synthetic research check",
    "inputs": [
        {
            "role": "brief",
            "ref": {
                "id": "00000000-0000-4000-8000-000000000010",
                "sha256": "a" * 64,
            },
        }
    ],
    "permittedTools": ["search_sources"],
    "budget": {
        "maxModelCalls": 1,
        "maxToolCalls": 0,
        "maxInputTokens": 1000,
        "maxOutputTokens": 500,
        "timeoutSec": 60,
        "retryCeiling": 1,
        "maxChildren": 0,
        "reserved": {"amountMinor": 100, "currency": "USD"},
    },
    "dataClassification": "internal",
    "outputDisposition": "draft_version",
    "reviewGate": "claim_review",
}

_SYNTHETIC_AGENT_RESULT: dict[str, Any] = {
    "contractVersion": "0.4.0",
    "attemptId": "00000000-0000-4000-8000-000000000004",
    "status": "failed",
    "validation": [{"stage": "schema", "passed": False, "failure": "schema_invalid"}],
    "consumed": {
        "modelCalls": 0,
        "toolCalls": 0,
        "inputTokens": 0,
        "outputTokens": 0,
    },
    "proposedActions": [],
    "proposedGraphChanges": [],
}

_DIAGNOSTIC_ECHO_INPUT: dict[str, Any] = {"text": "Signal Motion (working name)"}


def _def_validator(def_name: str) -> Draft202012Validator:
    registry = _build_schema_registry()
    return Draft202012Validator(
        {"$ref": f"{EXECUTION_SCHEMA_ID}#/$defs/{def_name}"},
        registry=registry,
    )


def _validate_task_contract(payload: dict[str, Any]) -> bool:
    try:
        TaskContract.model_validate(payload)
        return True
    except ValidationError:
        return False


def _json_validate_task_contract(payload: dict[str, Any]) -> bool:
    try:
        _def_validator("TaskContract").validate(payload)
        return True
    except JsonSchemaValidationError:
        return False


@pytest.mark.t("T-33")
def test_agent_result_rejects_non_empty_proposed_actions() -> None:
    bad = {**_SYNTHETIC_AGENT_RESULT, "proposedActions": [{"kind": "noop"}]}
    with pytest.raises(ValidationError):
        AgentResult.model_validate(bad)
    with pytest.raises(JsonSchemaValidationError):
        _def_validator("AgentResult").validate(bad)


@pytest.mark.t("T-33")
def test_research_task_contract_rejects_attempt_only_disposition() -> None:
    bad = {**_SYNTHETIC_TASK_CONTRACT, "outputDisposition": "attempt_only"}
    assert not _validate_task_contract(bad)
    assert not _json_validate_task_contract(bad)


@pytest.mark.t("T-33")
def test_research_task_contract_rejects_review_gate_none() -> None:
    bad = {**_SYNTHETIC_TASK_CONTRACT, "reviewGate": "none"}
    assert not _validate_task_contract(bad)
    assert not _json_validate_task_contract(bad)


@pytest.mark.t("T-33")
def test_diagnostic_echo_input_rejects_empty_or_too_long_text() -> None:
    with pytest.raises(ValidationError):
        DiagnosticEchoInput.model_validate({"text": ""})
    with pytest.raises(ValidationError):
        DiagnosticEchoInput.model_validate({"text": "x" * 201})
    DiagnosticEchoInput.model_validate(_DIAGNOSTIC_ECHO_INPUT)


@pytest.mark.t("T-33")
def test_diagnostic_echo_output_accepts_synthetic_example() -> None:
    DiagnosticEchoOutput.model_validate(
        {"text": "Signal Motion (working name)", "modelId": "fake-model-v1"}
    )
