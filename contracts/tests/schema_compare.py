"""Normalize JSON Schema documents for 0.4.0 equivalence checks (SPEC-03a AC3)."""

from __future__ import annotations

from typing import Any


def _normalize(node: Any) -> Any:
    if isinstance(node, dict):
        if "enum" in node and node.get("type") == "string":
            node = {key: value for key, value in node.items() if key != "type"}
        normalized: dict[str, Any] = {}
        for key in sorted(node):
            value = node[key]
            if key == "enum" and isinstance(value, list):
                normalized[key] = sorted(value)
            else:
                normalized[key] = _normalize(value)
        return normalized
    if isinstance(node, list):
        return [_normalize(item) for item in node]
    return node


def normalize_schema(document: dict[str, Any]) -> dict[str, Any]:
    return _normalize(document)


def schema_diff(
    expected: dict[str, Any],
    actual: dict[str, Any],
) -> list[str]:
    expected_norm = normalize_schema(expected)
    actual_norm = normalize_schema(actual)
    paths: list[str] = []

    def walk(path: str, left: Any, right: Any) -> None:
        if left == right:
            return
        if isinstance(left, dict) and isinstance(right, dict):
            keys = sorted(set(left) | set(right))
            for key in keys:
                child = f"{path}.{key}" if path else key
                if key not in left:
                    paths.append(f"missing in expected: {child}")
                elif key not in right:
                    paths.append(f"missing in actual: {child}")
                else:
                    walk(child, left[key], right[key])
            return
        paths.append(f"{path}: {left!r} != {right!r}")

    walk("", expected_norm, actual_norm)
    return paths
