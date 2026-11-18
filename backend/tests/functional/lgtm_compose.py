"""Read the compose.yaml lgtm service definition for SPEC-08 functional tests."""

from __future__ import annotations

from pathlib import Path

import yaml


def lgtm_service_spec(root: Path) -> dict:
    return yaml.safe_load((root / "compose.yaml").read_text())["services"]["lgtm"]


def mount_configured_volumes(container, *, mount_root: Path, spec: dict):
    for entry in spec.get("volumes", []):
        if not isinstance(entry, str) or entry.startswith("lgtm:"):
            continue
        parts = entry.split(":")
        if len(parts) < 2:
            continue
        host_path = parts[0]
        container_path = parts[1]
        if host_path.startswith("./"):
            host_path = mount_root / host_path.removeprefix("./")
        container = container.with_volume_mapping(Path(host_path), container_path)
    return container
