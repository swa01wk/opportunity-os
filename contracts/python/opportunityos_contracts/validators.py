"""Shared Pydantic validators for contract models."""

from __future__ import annotations

from typing import Any

# RFC 3339 UTC with a Z suffix (matches JSON Schema date-time + Ajv strict UTC fixtures).
TIMESTAMP_PATTERN = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d{1,9})?Z$"
FX_RATE_PATTERN = r"^[0-9]+(\.[0-9]+)?$"


def reject_explicit_null_keys(data: Any, field_names: frozenset[str]) -> Any:
    """Reject JSON null on optional fields; omission remains allowed (NFR-19)."""
    if not isinstance(data, dict):
        return data
    for key, value in data.items():
        if value is None and key in field_names:
            msg = f"{key} must be omitted, not null"
            raise ValueError(msg)
    return data
