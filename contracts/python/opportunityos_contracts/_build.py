"""Regenerate JSON Schema and drive TypeScript codegen (ADR-008)."""

from __future__ import annotations

import json
from enum import StrEnum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, TypeAdapter

from opportunityos_contracts.agui.stream import (
    AGUI_DEF_MODELS,
    AGUI_STREAM_DESCRIPTION,
    AGUI_STREAM_TITLE,
    STEP_NAME_PATTERN,
    agui_x_block,
)
from opportunityos_contracts.analytics.events import (
    ANALYTICS_DEF_MODELS,
    AnalyticsEvent,
    AnalyticsEventName,
    analytics_property_dispatch_rules,
)
from opportunityos_contracts.common import COMMON_DEF_ALIASES, COMMON_DEF_MODELS
from opportunityos_contracts.events.domain_event import (
    DOMAIN_DEF_MODELS,
    DomainEvent,
    DomainEventSubject,
    domain_payload_dispatch_rules,
)
from opportunityos_contracts.events.workflow_request import WorkflowRequest
from opportunityos_contracts.validators import TIMESTAMP_PATTERN

# Pydantic cannot set these on export; the generator adds only the following post-processing:
# - envelope metadata ($schema, $id, x-version, title, description) on each schema file
# - $ref rewriting from #/$defs/{Name} to ../common.schema.json#/$defs/{Name}
#   on schemas outside common.schema.json
# - inlining of workflow-local $defs so workflow-request matches the 0.4.0 shape (no $defs block)
# - recursive key ordering for deterministic bytes (AC1)
# - replace inlined primitive patterns with #/$defs/... refs (same logical type as $ref rewrite)
# - ge/le → minimum/maximum (draft 2020-12; Pydantic may emit ge on annotated ints)
COMMON_NAMES = frozenset({*COMMON_DEF_MODELS.keys(), *COMMON_DEF_ALIASES.keys()})
UUID_PATTERN = r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
LOCALID_PATTERN = r"^[a-z][a-z0-9_.-]{0,63}$"
SHA256_PATTERN = r"^[0-9a-f]{64}$"

REPO_ROOT = Path(__file__).resolve().parents[3]

COMMON_SCHEMA_ID = "https://opportunityos.invalid/contracts/common.schema.json"
WORKFLOW_SCHEMA_ID = "https://opportunityos.invalid/contracts/events/workflow-request.schema.json"
DOMAIN_EVENT_SCHEMA_ID = "https://opportunityos.invalid/contracts/events/domain-event.schema.json"
AGUI_STREAM_ID = "https://opportunityos.invalid/contracts/agui/stream.json"
ANALYTICS_SCHEMA_ID = "https://opportunityos.invalid/contracts/analytics/events.schema.json"

BASELINES = REPO_ROOT / "contracts" / "tests" / "baselines"

COMMON_META: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": COMMON_SCHEMA_ID,
    "x-version": "0.1.0",
    "title": "Common definitions",
    "description": (
        "Shared primitives used by every OpportunityOS contract. "
        "Canonical source from M0: Pydantic (ADR-008)."
    ),
}

DOMAIN_EVENT_META: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": DOMAIN_EVENT_SCHEMA_ID,
    "x-version": "0.4.0",
    "title": "DomainEvent",
    "type": "object",
    "additionalProperties": False,
}

ANALYTICS_EVENT_META: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": ANALYTICS_SCHEMA_ID,
    "x-version": "0.2.0",
    "title": "AnalyticsEvent",
    "type": "object",
    "additionalProperties": False,
}

WORKFLOW_META: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": WORKFLOW_SCHEMA_ID,
    "x-version": "0.4.0",
    "title": "WorkflowRequest",
    "description": (
        "Durable request written by the API in the same transaction as the command (ADR-003). "
        "The dispatcher starts a DBOS workflow whose ID equals requestId, so lost "
        "acknowledgements and duplicate dispatch start at most one workflow."
    ),
    "type": "object",
    "additionalProperties": False,
}


def _polish_schema(node: Any) -> Any:
    if isinstance(node, dict):
        node = {key: _polish_schema(value) for key, value in node.items()}
        if "ge" in node:
            node["minimum"] = node.pop("ge")
        if "le" in node:
            node["maximum"] = node.pop("le")
        if "gt" in node and node.get("type") == "number":
            node["exclusiveMinimum"] = node.pop("gt")
        node.pop("title", None)
        return node
    if isinstance(node, list):
        return [_polish_schema(item) for item in node]
    return node


def _sort_keys(node: Any) -> Any:
    if isinstance(node, dict):
        return {key: _sort_keys(node[key]) for key in sorted(node)}
    if isinstance(node, list):
        return [_sort_keys(item) for item in node]
    return node


def _format_json(value: Any) -> str:
    return json.dumps(_sort_keys(value), indent=2, ensure_ascii=False) + "\n"


def _export_def_schema(model: type[BaseModel] | type) -> dict[str, Any]:
    if isinstance(model, type) and issubclass(model, BaseModel):
        raw = model.model_json_schema(mode="serialization", ref_template="#/$defs/{model}")
        local_defs = dict(raw.pop("$defs", {}))
        inlined = _inline_local_refs(raw, local_defs)
        if not isinstance(inlined, dict):
            msg = f"expected dict schema for {model}"
            raise TypeError(msg)
        return inlined
    schema = TypeAdapter(model).json_schema(ref_template="#/$defs/{model}")
    if not isinstance(schema, dict):
        msg = f"expected dict schema for {model}"
        raise TypeError(msg)
    return schema


def _inline_local_refs(
    node: Any,
    local_defs: dict[str, Any],
    *,
    preserve: frozenset[str] | None = None,
) -> Any:
    keep = preserve or frozenset()
    if isinstance(node, dict):
        ref = node.get("$ref")
        if isinstance(ref, str) and ref.startswith("#/$defs/"):
            name = ref.removeprefix("#/$defs/")
            if name in keep:
                return node
            if name in local_defs:
                resolved = _inline_local_refs(local_defs[name], local_defs, preserve=keep)
                if isinstance(resolved, dict) and "description" in node:
                    resolved = dict(resolved)
                    resolved["description"] = node["description"]
                return resolved
        return {
            key: _inline_local_refs(value, local_defs, preserve=keep) for key, value in node.items()
        }
    if isinstance(node, list):
        return [_inline_local_refs(item, local_defs, preserve=keep) for item in node]
    return node


def _common_ref(name: str, *, external: bool) -> dict[str, str]:
    if external:
        return {"$ref": f"../common.schema.json#/$defs/{name}"}
    return {"$ref": f"#/$defs/{name}"}


def _pattern_common_ref(node: dict[str, Any], *, external: bool) -> dict[str, str] | None:
    if node.get("type") != "string":
        return None
    pattern = node.get("pattern")
    if pattern == UUID_PATTERN:
        name = "Uuid"
    elif pattern == LOCALID_PATTERN:
        name = "LocalId"
    elif pattern == SHA256_PATTERN:
        name = "Sha256"
    elif pattern == TIMESTAMP_PATTERN:
        name = "Timestamp"
    else:
        return None
    if external:
        return {"$ref": f"../common.schema.json#/$defs/{name}"}
    return {"$ref": f"#/$defs/{name}"}


def _rewrite_common_refs(node: Any, *, external: bool) -> Any:
    if isinstance(node, dict):
        ref = node.get("$ref")
        if isinstance(ref, str) and ref.startswith("#/$defs/"):
            name = ref.removeprefix("#/$defs/")
            if name in COMMON_NAMES:
                if external:
                    return {"$ref": f"../common.schema.json#/$defs/{name}"}
                return {"$ref": f"#/$defs/{name}"}
        pattern_ref = _pattern_common_ref(node, external=external)
        allowed = {"type", "pattern", "format", "description", "title"}
        if pattern_ref is not None and set(node.keys()) <= allowed:
            return pattern_ref
        return {key: _rewrite_common_refs(value, external=external) for key, value in node.items()}
    if isinstance(node, list):
        return [_rewrite_common_refs(item, external=external) for item in node]
    return node


def _build_common_document() -> dict[str, Any]:
    defs = {
        name: _rewrite_common_refs(_export_def_schema(model), external=False)
        for name, model in COMMON_DEF_MODELS.items()
    }
    for name, alias in COMMON_DEF_ALIASES.items():
        defs[name] = _export_def_schema(alias)
    return {**COMMON_META, "$defs": defs}


_INPUT_COMMON_REFS: dict[str, str] = {
    "contractRef": "VersionRef",
    "scriptRef": "VersionRef",
    "storyboardRef": "VersionRef",
    "packageRef": "VersionRef",
    "estimatedCost": "Money",
    "revisionId": "Uuid",
}


def _workflow_input_common_refs(input_schema: dict[str, Any]) -> None:
    properties = input_schema.get("properties")
    if not isinstance(properties, dict):
        return
    for key, def_name in _INPUT_COMMON_REFS.items():
        if key not in properties:
            continue
        current = properties[key]
        description = current.get("description") if isinstance(current, dict) else None
        ref: dict[str, Any] = {"$ref": f"../common.schema.json#/$defs/{def_name}"}
        if key == "estimatedCost" and description:
            ref["description"] = description
        properties[key] = ref


def _load_baseline(name: str) -> dict[str, Any]:
    loaded: object = json.loads((BASELINES / name).read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        msg = f"baseline {name} is not a JSON object"
        raise TypeError(msg)
    return loaded


def _model_description(model: type) -> str:
    doc = (model.__doc__ or "").strip()
    return " ".join(part.strip() for part in doc.splitlines() if part.strip())


def _build_if_then_dispatch(
    rules: list[tuple[list[str], str]],
    *,
    discriminator: str,
    target_property: str,
) -> list[dict[str, Any]]:
    blocks: list[dict[str, Any]] = []
    for values, ref in rules:
        type_schema: dict[str, Any] = {"const": values[0]} if len(values) == 1 else {"enum": values}
        blocks.append(
            {
                "if": {"properties": {discriminator: type_schema}},
                "then": {"properties": {target_property: {"$ref": ref}}},
            }
        )
    return blocks


def _export_inline_model(
    model: type[BaseModel],
    *,
    external: bool,
    preserve: frozenset[str],
) -> dict[str, Any]:
    raw = model.model_json_schema(mode="serialization", ref_template="#/$defs/{model}")
    local_defs = dict(raw.pop("$defs", {}))
    body = _inline_local_refs(raw, local_defs, preserve=preserve)
    polished = _polish_schema(_rewrite_common_refs(body, external=external))
    if not isinstance(polished, dict):
        msg = f"expected dict schema for {model}"
        raise TypeError(msg)
    return polished


def _export_root_envelope(
    model: type[BaseModel],
    *,
    meta: dict[str, Any],
    external: bool,
    preserve: frozenset[str],
    property_overrides: dict[str, Any],
    comment: str | None = None,
) -> dict[str, Any]:
    raw = model.model_json_schema(mode="serialization", ref_template="#/$defs/{model}")
    local_defs = dict(raw.pop("$defs", {}))
    properties: dict[str, Any] = {}
    for key, value in raw.get("properties", {}).items():
        if key in property_overrides:
            continue
        inlined = _inline_local_refs(value, local_defs, preserve=preserve)
        properties[key] = _polish_schema(_rewrite_common_refs(inlined, external=external))
    properties.update(property_overrides)
    for key in ("requestId", "projectId", "workspaceId", "eventId", "sourceEventId", "memberId"):
        if key in properties:
            properties[key] = _common_ref("Uuid", external=external)
    if "occurredAt" in properties:
        properties["occurredAt"] = _common_ref("Timestamp", external=external)
    if "requestedBy" in properties:
        properties["requestedBy"] = _common_ref("Actor", external=external)
    if "actor" in properties:
        properties["actor"] = _common_ref("Actor", external=external)
    if "correlationId" in properties and isinstance(properties["correlationId"], dict):
        properties["correlationId"] = {
            **_common_ref("Uuid", external=external),
            "description": "Run or request that this event belongs to.",
        }
    if "causationId" in properties and isinstance(properties["causationId"], dict):
        properties["causationId"] = {
            **_common_ref("Uuid", external=external),
            "description": "Event or command that caused this one.",
        }
    document: dict[str, Any] = {
        **meta,
        "description": _model_description(model),
        "required": list(raw.get("required", [])),
        "properties": properties,
    }
    if comment:
        document["$comment"] = comment
    extra = model.model_config.get("json_schema_extra")
    if isinstance(extra, dict) and "$comment" in extra and comment is None:
        document["$comment"] = extra["$comment"]
    return document


def _export_registry_defs(
    models: dict[str, type],
    *,
    external: bool,
) -> dict[str, Any]:
    preserve = frozenset(models) | COMMON_NAMES
    defs: dict[str, Any] = {}
    for name, model in models.items():
        if isinstance(model, type) and issubclass(model, StrEnum):
            defs[name] = {"enum": [member.value for member in model]}
            continue
        if not isinstance(model, type) or not issubclass(model, BaseModel):
            schema = TypeAdapter(model).json_schema(ref_template="#/$defs/{model}")
            defs[name] = _polish_schema(_rewrite_common_refs(schema, external=external))
            continue
        raw = model.model_json_schema(mode="serialization", ref_template="#/$defs/{model}")
        local_defs = dict(raw.pop("$defs", {}))
        body = _inline_local_refs(raw, local_defs, preserve=preserve)
        defs[name] = _polish_schema(_rewrite_common_refs(body, external=external))
    return defs


def _merge_baseline_document(baseline_name: str, defs: dict[str, Any]) -> dict[str, Any]:
    document = _load_baseline(baseline_name)
    document["$defs"] = defs
    return document


def _build_domain_event_document() -> dict[str, Any]:
    preserve = frozenset(DOMAIN_DEF_MODELS) | COMMON_NAMES
    defs = _export_registry_defs(DOMAIN_DEF_MODELS, external=True)
    subject = _export_inline_model(DomainEventSubject, external=True, preserve=preserve)
    overrides = {
        "type": {"$ref": "#/$defs/EventType"},
        "eventVersion": {
            "type": "integer",
            "minimum": 1,
            "description": "Payload version for this type.",
        },
        "subject": subject,
        "payload": {"type": "object"},
    }
    envelope = _export_root_envelope(
        DomainEvent,
        meta=DOMAIN_EVENT_META,
        external=True,
        preserve=preserve,
        property_overrides=overrides,
    )
    envelope["allOf"] = _build_if_then_dispatch(
        domain_payload_dispatch_rules(),
        discriminator="type",
        target_property="payload",
    )
    envelope["$defs"] = defs
    return envelope


def _strip_nullable_default(defs: dict[str, Any], def_name: str, property_name: str) -> None:
    definition = defs.get(def_name)
    if not isinstance(definition, dict):
        return
    properties = definition.get("properties")
    if not isinstance(properties, dict):
        return
    field = properties.get(property_name)
    if isinstance(field, dict):
        field.pop("default", None)


def _build_analytics_document() -> dict[str, Any]:
    preserve = frozenset(ANALYTICS_DEF_MODELS) | COMMON_NAMES
    defs = _export_registry_defs(ANALYTICS_DEF_MODELS, external=True)
    _strip_nullable_default(defs, "metric_recorded", "value")
    overrides = {
        "eventName": {"enum": [member.value for member in AnalyticsEventName]},
        "properties": {"type": "object"},
    }
    envelope = _export_root_envelope(
        AnalyticsEvent,
        meta=ANALYTICS_EVENT_META,
        external=True,
        preserve=preserve,
        property_overrides=overrides,
    )
    envelope["allOf"] = _build_if_then_dispatch(
        analytics_property_dispatch_rules(),
        discriminator="eventName",
        target_property="properties",
    )
    envelope["$defs"] = defs
    return envelope


def _build_agui_stream_document() -> dict[str, Any]:
    defs = _export_registry_defs(AGUI_DEF_MODELS, external=True)
    defs["RunErrorCode"] = {"$ref": "../common.schema.json#/$defs/ErrorClass"}
    gate_ref = "../events/domain-event.schema.json#/$defs/Gate"
    run_paused = defs.get("RunPaused")
    if isinstance(run_paused, dict):
        properties = run_paused.get("properties")
        if isinstance(properties, dict) and "gate" in properties:
            gate = properties["gate"]
            if isinstance(gate, dict):
                gate.clear()
                gate["$ref"] = gate_ref
                gate["description"] = "Set when reason = awaiting_approval."
    project_run_state = defs.get("ProjectRunState")
    if isinstance(project_run_state, dict):
        properties = project_run_state.get("properties")
        if isinstance(properties, dict) and "productionState" in properties:
            properties["productionState"] = {
                "$ref": "../events/domain-event.schema.json#/$defs/ProductionState"
            }
    step_name = defs.get("StepName")
    if isinstance(step_name, dict):
        step_name["pattern"] = STEP_NAME_PATTERN
        if step_name.get("type") is None:
            step_name["type"] = "string"
    active_run = defs.get("ProjectRunState", {}).get("properties", {}).get("activeRuns", {})
    items: dict[str, Any] = {}
    if isinstance(active_run, dict):
        items_maybe = active_run.get("items", {}).get("properties", {})
        if isinstance(items_maybe, dict):
            items = items_maybe
    if isinstance(items, dict) and "currentStep" in items:
        items["currentStep"] = {"$ref": "#/$defs/StepName"}
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": AGUI_STREAM_ID,
        "x-version": "0.4.0",
        "title": AGUI_STREAM_TITLE,
        "description": AGUI_STREAM_DESCRIPTION,
        "x-agui": agui_x_block(),
        "$defs": defs,
    }


def _build_workflow_document() -> dict[str, Any]:
    raw = WorkflowRequest.model_json_schema(mode="serialization", ref_template="#/$defs/{model}")
    local_defs = dict(raw.pop("$defs", {}))
    properties = {
        key: _rewrite_common_refs(
            _inline_local_refs(value, local_defs),
            external=True,
        )
        for key, value in raw.get("properties", {}).items()
    }
    if isinstance(properties.get("input"), dict):
        _workflow_input_common_refs(properties["input"])
    for key in ("requestId", "projectId"):
        if key in properties:
            properties[key] = _common_ref("Uuid", external=True)
    if "requestedBy" in properties:
        properties["requestedBy"] = _common_ref("Actor", external=True)
    if "notBefore" in properties:
        properties["notBefore"] = _common_ref("Timestamp", external=True)
    workflow_type = properties.get("workflowType")
    if isinstance(workflow_type, dict):
        workflow_type.pop("type", None)
    return {
        **WORKFLOW_META,
        "required": list(raw.get("required", [])),
        "properties": properties,
    }


def generate(output_root: Path | None = None) -> None:
    root = output_root or REPO_ROOT
    common_path = root / "docs" / "contracts" / "common.schema.json"
    workflow_path = root / "docs" / "contracts" / "events" / "workflow-request.schema.json"
    domain_event_path = root / "docs" / "contracts" / "events" / "domain-event.schema.json"
    agui_path = root / "docs" / "contracts" / "agui" / "stream.json"
    analytics_path = root / "docs" / "contracts" / "analytics" / "events.schema.json"
    common_path.parent.mkdir(parents=True, exist_ok=True)
    workflow_path.parent.mkdir(parents=True, exist_ok=True)
    agui_path.parent.mkdir(parents=True, exist_ok=True)
    analytics_path.parent.mkdir(parents=True, exist_ok=True)
    common_doc = _build_common_document()
    common_doc["$defs"] = _polish_schema(common_doc["$defs"])
    workflow_doc = _build_workflow_document()
    workflow_doc["properties"] = _polish_schema(workflow_doc["properties"])
    domain_doc = _format_json(_build_domain_event_document())
    agui_doc = _format_json(_build_agui_stream_document())
    analytics_doc = _format_json(_build_analytics_document())
    common_path.write_text(_format_json(common_doc), encoding="utf-8")
    workflow_path.write_text(_format_json(workflow_doc), encoding="utf-8")
    domain_event_path.write_text(domain_doc, encoding="utf-8")
    agui_path.write_text(agui_doc, encoding="utf-8")
    analytics_path.write_text(analytics_doc, encoding="utf-8")


def main() -> None:
    generate()
    print(
        "contracts: regenerated common, workflow-request, domain-event, "
        "agui/stream and analytics/events schemas"
    )


if __name__ == "__main__":
    main()
