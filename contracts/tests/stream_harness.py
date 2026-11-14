"""Validate recorded AG-UI streams against stream.json $defs (SPEC-03b AC2)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fixture_harness import _build_schema_registry
from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError as JsonSchemaValidationError
from pydantic import TypeAdapter, ValidationError

from opportunityos_contracts.agui.stream import (
    ProjectRunState,
    RenderProgress,
    RunPaused,
    StepName,
    ToolCallArgsSummary,
    ToolCallResultSummary,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
STREAM_SCHEMA_PATH = REPO_ROOT / "docs" / "contracts" / "agui" / "stream.json"
STREAM_DEFS = json.loads(STREAM_SCHEMA_PATH.read_text(encoding="utf-8"))["$defs"]


def _parse_seq(seq: str) -> tuple[int, int]:
    if "." in seq:
        head, tail = seq.split(".", 1)
        return int(head), int(tail)
    return int(seq), 0


def seqs_increase(lines: list[dict[str, Any]]) -> bool:
    prev = (-1, -1)
    for line in lines:
        seq = line.get("seq")
        if not isinstance(seq, str):
            return False
        try:
            current = _parse_seq(seq)
        except ValueError:
            return False
        if current <= prev:
            return False
        prev = current
    return True


def _ajv_validate(defn_name: str, payload: Any) -> bool:
    registry = _build_schema_registry()
    document = json.loads(STREAM_SCHEMA_PATH.read_text(encoding="utf-8"))
    schema = {
        "$schema": document["$schema"],
        "$id": document["$id"],
        "$defs": document["$defs"],
        "$ref": f"#/$defs/{defn_name}",
    }
    validator = Draft202012Validator(schema, registry=registry)
    try:
        validator.validate(payload)
        return True
    except JsonSchemaValidationError:
        return False


def _pydantic_validate(defn_name: str, payload: dict[str, Any]) -> bool:
    models: dict[str, type] = {
        "ProjectRunState": ProjectRunState,
        "RenderProgress": RenderProgress,
        "RunPaused": RunPaused,
        "ToolCallArgsSummary": ToolCallArgsSummary,
        "ToolCallResultSummary": ToolCallResultSummary,
    }
    try:
        if defn_name == "StepName":
            TypeAdapter(StepName).validate_python(payload)
            return True
        models[defn_name].model_validate(payload)
        return True
    except ValidationError:
        return False


def validate_frame_payload(data: dict[str, Any]) -> tuple[bool, bool]:
    """Return (pydantic_ok, ajv_ok) for the parts this contract owns."""
    event_type = data.get("type")
    if not isinstance(event_type, str):
        return False, False

    if event_type == "STATE_SNAPSHOT":
        snapshot = data.get("snapshot")
        if not isinstance(snapshot, dict):
            return False, False
        return (
            _pydantic_validate("ProjectRunState", snapshot),
            _ajv_validate("ProjectRunState", snapshot),
        )

    if event_type in {"STEP_STARTED", "STEP_FINISHED"}:
        step = data.get("stepName")
        if not isinstance(step, str):
            return False, False
        pydantic_ok = _pydantic_validate("StepName", step)
        ajv_ok = _ajv_validate("StepName", step)
        return pydantic_ok, ajv_ok

    if event_type in {"ACTIVITY_SNAPSHOT", "ACTIVITY_DELTA"}:
        content = data.get("content")
        activity = data.get("activityType")
        if not isinstance(content, dict) or not isinstance(activity, str):
            return False, False
        def_name = "RenderProgress" if activity == "opportunityos.render_progress" else "RunPaused"
        return _pydantic_validate(def_name, content), _ajv_validate(def_name, content)

    if event_type == "TOOL_CALL_ARGS":
        delta = data.get("delta")
        if not isinstance(delta, str):
            return False, False
        try:
            parsed = json.loads(delta)
        except json.JSONDecodeError:
            return False, False
        if not isinstance(parsed, dict):
            return False, False
        return (
            _pydantic_validate("ToolCallArgsSummary", parsed),
            _ajv_validate("ToolCallArgsSummary", parsed),
        )

    if event_type == "TOOL_CALL_RESULT":
        content = data.get("content")
        if not isinstance(content, str):
            return False, False
        try:
            parsed = json.loads(content)
        except json.JSONDecodeError:
            return False, False
        if not isinstance(parsed, dict):
            return False, False
        return (
            _pydantic_validate("ToolCallResultSummary", parsed),
            _ajv_validate("ToolCallResultSummary", parsed),
        )

    if event_type == "CUSTOM":
        value = data.get("value")
        if isinstance(value, dict) and "$comment" in value:
            return True, True

    if event_type in {
        "RUN_STARTED",
        "RUN_FINISHED",
        "RUN_ERROR",
        "TOOL_CALL_START",
        "TOOL_CALL_END",
    }:
        return True, True

    return True, True


def load_stream_lines(path: Path) -> list[dict[str, Any]]:
    lines: list[dict[str, Any]] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        if not raw.strip():
            continue
        parsed = json.loads(raw)
        if not isinstance(parsed, dict):
            msg = f"stream line is not an object in {path}"
            raise TypeError(msg)
        lines.append(parsed)
    return lines


def validate_stream_file(path: Path) -> tuple[bool, bool, bool]:
    lines = load_stream_lines(path)
    seq_ok = seqs_increase(lines)
    pydantic_ok = True
    ajv_ok = True
    for line in lines:
        data = line.get("data")
        if not isinstance(data, dict):
            pydantic_ok = False
            ajv_ok = False
            continue
        p_ok, j_ok = validate_frame_payload(data)
        pydantic_ok = pydantic_ok and p_ok
        ajv_ok = ajv_ok and j_ok
    return seq_ok, pydantic_ok, ajv_ok
