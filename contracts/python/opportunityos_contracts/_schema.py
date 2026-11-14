"""JSON Schema export helpers (canonical on the Pydantic models, ADR-008)."""

from __future__ import annotations

from typing import Any, cast

from pydantic import BaseModel
from pydantic.json_schema import JsonSchemaValue


def strip_omit_only_null_unions(node: Any) -> Any:
    """Optional contract fields may be omitted; explicit JSON null is rejected in validation."""
    if isinstance(node, dict):
        if "anyOf" in node:
            options = node["anyOf"]
            non_null = [
                item
                for item in options
                if not (isinstance(item, dict) and item.get("type") == "null")
            ]
            if len(non_null) == 1 and len(non_null) < len(options):
                merged = strip_omit_only_null_unions(non_null[0])
                if isinstance(merged, dict):
                    for key, value in node.items():
                        if key in {"anyOf", "default", "title"}:
                            continue
                        merged[key] = strip_omit_only_null_unions(value)
                    return merged
                return merged
        return {key: strip_omit_only_null_unions(value) for key, value in node.items()}
    if isinstance(node, list):
        return [strip_omit_only_null_unions(item) for item in node]
    return node


class ContractModel(BaseModel):
    @classmethod
    def __get_pydantic_json_schema__(
        cls,
        core_schema: Any,
        handler: Any,
    ) -> JsonSchemaValue:
        schema = handler(core_schema)
        return cast("dict[str, Any]", strip_omit_only_null_unions(schema))
