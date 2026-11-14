"""Regenerate JSON Schema and drive TypeScript codegen (ADR-008)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, TypeAdapter

from opportunityos_contracts.common import COMMON_DEF_ALIASES, COMMON_DEF_MODELS
from opportunityos_contracts.events.workflow_request import WorkflowRequest, WorkflowType

COMMON_NAMES = frozenset({*COMMON_DEF_MODELS.keys(), *COMMON_DEF_ALIASES.keys()})
UUID_PATTERN = r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
LOCALID_PATTERN = r"^[a-z][a-z0-9_.-]{0,63}$"
SHA256_PATTERN = r"^[0-9a-f]{64}$"

REPO_ROOT = Path(__file__).resolve().parents[3]

COMMON_SCHEMA_ID = "https://opportunityos.invalid/contracts/common.schema.json"
WORKFLOW_SCHEMA_ID = "https://opportunityos.invalid/contracts/events/workflow-request.schema.json"

COMMON_META = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": COMMON_SCHEMA_ID,
    "x-version": "0.1.0",
    "title": "Common definitions",
    "description": (
        "Shared primitives used by every OpportunityOS contract. "
        "Canonical source from M0: Pydantic (ADR-008)."
    ),
}

WORKFLOW_META = {
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


def _format_json(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def _def_schema(name: str, schema: dict[str, Any]) -> dict[str, Any]:
    schema = dict(schema)
    schema.pop("$schema", None)
    schema.pop("$id", None)
    schema.pop("title", None)
    if schema.get("type") == "string" and "enum" in schema:
        schema["enum"] = list(schema["enum"])
    if "description" in schema and schema["description"] == name:
        schema.pop("description", None)
    if schema.get("type") == "object" and schema.get("additionalProperties") is False:
        schema["additionalProperties"] = False
    return schema


def _common_ref(name: str, *, external: bool) -> dict[str, str]:
    if external:
        return {"$ref": f"../common.schema.json#/$defs/{name}"}
    return {"$ref": f"#/$defs/{name}"}


def _resolve_schema_node(
    node: Any,
    local_defs: dict[str, Any],
    *,
    external_common: bool = False,
) -> Any:
    if isinstance(node, dict):
        ref = node.get("$ref")
        if isinstance(ref, str) and ref.startswith("#/$defs/"):
            name = ref.removeprefix("#/$defs/")
            if name in COMMON_NAMES:
                return _common_ref(name, external=external_common)
            if name in local_defs:
                return _resolve_schema_node(
                    local_defs[name],
                    local_defs,
                    external_common=external_common,
                )
        if node.get("type") == "string" and node.get("pattern") == UUID_PATTERN:
            return _common_ref("Uuid", external=external_common)
        if node.get("type") == "string" and node.get("pattern") == LOCALID_PATTERN:
            return _common_ref("LocalId", external=external_common)
        if node.get("type") == "string" and node.get("pattern") == SHA256_PATTERN:
            return _common_ref("Sha256", external=external_common)
        if "anyOf" in node:
            options = node["anyOf"]
            non_null = [
                item
                for item in options
                if not (isinstance(item, dict) and item.get("type") == "null")
            ]
            has_null = len(non_null) < len(options)
            if has_null and len(non_null) == 1:
                return _resolve_schema_node(
                    non_null[0],
                    local_defs,
                    external_common=external_common,
                )
        resolved = {
            key: _resolve_schema_node(value, local_defs, external_common=external_common)
            for key, value in node.items()
        }
        resolved.pop("default", None)
        resolved.pop("title", None)
        return resolved
    if isinstance(node, list):
        return [
            _resolve_schema_node(item, local_defs, external_common=external_common) for item in node
        ]
    return node


def _build_common_defs() -> dict[str, Any]:
    defs: dict[str, Any] = {}
    for name, model in COMMON_DEF_MODELS.items():
        if isinstance(model, type) and issubclass(model, BaseModel):
            raw = model.model_json_schema(mode="serialization", ref_template="#/$defs/{model}")
            local_defs = dict(raw.pop("$defs", {}))
            resolved = _resolve_schema_node(raw, local_defs, external_common=False)
        else:
            resolved = TypeAdapter(model).json_schema(ref_template="#/$defs/{model}")
        defs[name] = _def_schema(name, resolved)
    for name, alias in COMMON_DEF_ALIASES.items():
        raw = TypeAdapter(alias).json_schema(ref_template="#/$defs/{model}")
        defs[name] = _def_schema(name, raw)
        if name == "Uuid":
            defs[name]["format"] = "uuid"
        if name == "Timestamp":
            defs[name]["format"] = "date-time"
    _attach_common_descriptions(defs)
    return defs


def _attach_common_descriptions(defs: dict[str, Any]) -> None:
    defs["Sha256"]["description"] = (
        "Lowercase hex SHA-256 of canonical JSON (RFC 8785) or of file bytes."
    )
    defs["Timestamp"]["description"] = (
        "Absolute UTC timestamp (RFC 3339). Display timezone is a destination setting (R-04)."
    )
    defs["LocalId"]["description"] = (
        "Stable, human-readable ID unique within its document "
        "(objects, elements, scenes, beats, phrases)."
    )
    defs["Token"]["description"] = (
        "Design-token name from docs/design/tokens.md, e.g. color.layer.3 or ease.standard. "
        "Never a raw value."
    )
    defs["Money"]["properties"]["amountMinor"]["description"] = (
        "Amount in minor units (paise, cents)."
    )
    defs["Money"]["properties"]["fxRateToReporting"] = {
        "type": "string",
        "pattern": "^[0-9]+(\\.[0-9]+)?$",
        "description": (
            "Recorded conversion rate into the reporting currency (INR, Q-05), as a decimal string."
        ),
    }
    defs["VersionRef"]["description"] = (
        "Pointer to one immutable version of a record. Approvals and manifests bind to these."
    )
    defs["BlobRef"]["description"] = "Content-addressed object in private storage (ADR-007)."
    defs["Actor"]["properties"]["responsibility"]["description"] = (
        "PRD §2.3 responsibility the action was taken under (R-05). Only members have one."
    )
    defs["ErrorClass"]["description"] = (
        "R-53 classification. Each class has its own repair options."
    )
    defs["ErrorTarget"]["properties"]["field"]["description"] = (
        "JSON pointer into the failing document."
    )


def _build_workflow_schema(_common_defs: dict[str, Any]) -> dict[str, Any]:
    raw = WorkflowRequest.model_json_schema(
        mode="serialization",
        ref_template="#/$defs/{model}",
    )
    local_defs = dict(raw.get("$defs", {}))
    properties = raw.get("properties", {})
    resolved_properties: dict[str, Any] = {}
    for json_name, prop in properties.items():
        if json_name == "workflowType":
            resolved_properties[json_name] = {"enum": [member.value for member in WorkflowType]}
            continue
        if json_name == "notBefore":
            resolved_properties[json_name] = _common_ref("Timestamp", external=True)
            continue
        resolved = _resolve_schema_node(prop, local_defs, external_common=True)
        if json_name == "input" and isinstance(resolved, dict):
            inner_props = resolved.get("properties", {})
            if "estimatedCost" in inner_props:
                inner_props["estimatedCost"] = {
                    "$ref": "../common.schema.json#/$defs/Money",
                    "description": (
                        "Run estimate checked against the remaining allowance at "
                        "request time (R-07). Each task still reserves its own "
                        "cost before dispatch (R-34)."
                    ),
                }
        resolved_properties[json_name] = resolved
    return {
        **WORKFLOW_META,
        "required": list(raw.get("required", [])),
        "properties": resolved_properties,
    }


def _write_schema(path: Path, document: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_format_json(document), encoding="utf-8")


def generate() -> None:
    common_defs = _build_common_defs()
    common_doc = {**COMMON_META, "$defs": common_defs}
    workflow_doc = _build_workflow_schema(common_defs)

    _write_schema(REPO_ROOT / "docs" / "contracts" / "common.schema.json", common_doc)
    _write_schema(
        REPO_ROOT / "docs" / "contracts" / "events" / "workflow-request.schema.json",
        workflow_doc,
    )


def main() -> None:
    generate()
    print("contracts: regenerated common.schema.json and events/workflow-request.schema.json")


if __name__ == "__main__":
    main()
