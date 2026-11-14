"""Regenerate JSON Schema and drive TypeScript codegen (ADR-008)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, TypeAdapter

from opportunityos_contracts.common import COMMON_DEF_ALIASES, COMMON_DEF_MODELS
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


def _inline_local_refs(node: Any, local_defs: dict[str, Any]) -> Any:
    if isinstance(node, dict):
        ref = node.get("$ref")
        if isinstance(ref, str) and ref.startswith("#/$defs/"):
            name = ref.removeprefix("#/$defs/")
            if name in local_defs:
                resolved = _inline_local_refs(local_defs[name], local_defs)
                if isinstance(resolved, dict) and "description" in node:
                    resolved = dict(resolved)
                    resolved["description"] = node["description"]
                return resolved
        return {key: _inline_local_refs(value, local_defs) for key, value in node.items()}
    if isinstance(node, list):
        return [_inline_local_refs(item, local_defs) for item in node]
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
    common_path.parent.mkdir(parents=True, exist_ok=True)
    workflow_path.parent.mkdir(parents=True, exist_ok=True)
    common_doc = _build_common_document()
    common_doc["$defs"] = _polish_schema(common_doc["$defs"])
    workflow_doc = _build_workflow_document()
    workflow_doc["properties"] = _polish_schema(workflow_doc["properties"])
    common_path.write_text(_format_json(common_doc), encoding="utf-8")
    workflow_path.write_text(_format_json(workflow_doc), encoding="utf-8")


def main() -> None:
    generate()
    print("contracts: regenerated common.schema.json and events/workflow-request.schema.json")


if __name__ == "__main__":
    main()
