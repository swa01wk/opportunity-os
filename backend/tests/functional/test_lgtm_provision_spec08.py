"""T-38: LGTM provisioning from compose.yaml (SPEC-08 AC4, R4)."""

from __future__ import annotations

import os
from pathlib import Path

import pytest
import requests
from lgtm_compose import lgtm_service_spec, mount_configured_volumes
from testcontainers.core.container import DockerContainer
from wait_http import wait_http_ready


def _checkout_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _docker_mount_root() -> Path:
    return Path(os.environ.get("OOS_HOST_REPO", _checkout_root()))


def _lgtm_image() -> str:
    for line in (_checkout_root() / "infra/images.env").read_text().splitlines():
        if line.startswith("LGTM_IMAGE="):
            return line.split("=", 1)[1].strip()
    msg = "LGTM_IMAGE missing from infra/images.env"
    raise RuntimeError(msg)


def _start_lgtm_from_compose() -> DockerContainer:
    spec = lgtm_service_spec(_checkout_root())
    mount_root = _docker_mount_root()
    container = DockerContainer(_lgtm_image()).with_exposed_ports(3000, 9090, 3100, 3200)
    for key, value in spec["environment"].items():
        container = container.with_env(key, value)
    mount_configured_volumes(container, mount_root=mount_root, spec=spec)
    return container


@pytest.fixture(scope="module")
def lgtm_endpoints() -> dict[str, str]:
    container = _start_lgtm_from_compose()
    container.start()
    host = container.get_container_host_ip()
    ports = {
        "grafana": container.get_exposed_port(3000),
        "prometheus": container.get_exposed_port(9090),
        "loki": container.get_exposed_port(3100),
        "tempo": container.get_exposed_port(3200),
    }
    wait_http_ready(f"http://{host}:{ports['grafana']}/api/health")
    endpoints = {name: f"http://{host}:{port}" for name, port in ports.items()}
    yield endpoints
    container.stop()


@pytest.mark.functional
@pytest.mark.t("T-38")
def test_compose_lgtm_env_matches_running_stack(lgtm_endpoints: dict[str, str]) -> None:
    spec = lgtm_service_spec(_checkout_root())
    assert "90d" in spec["environment"]["PROMETHEUS_EXTRA_ARGS"]
    assert "compactor.retention-enabled=true" in spec["environment"]["LOKI_EXTRA_ARGS"]
    res = requests.get(f"{lgtm_endpoints['prometheus']}/api/v1/status/flags", timeout=15)
    res.raise_for_status()
    assert res.json()["data"]["storage.tsdb.retention.time"] == "90d"


@pytest.mark.functional
@pytest.mark.t("T-38")
def test_grafana_lists_three_datasources(lgtm_endpoints: dict[str, str]) -> None:
    res = requests.get(
        f"{lgtm_endpoints['grafana']}/api/datasources",
        auth=("admin", "admin"),
        timeout=30,
    )
    res.raise_for_status()
    types = {entry["type"] for entry in res.json()}
    assert types >= {"prometheus", "loki", "tempo"}


@pytest.mark.functional
@pytest.mark.t("T-38")
def test_grafana_provisions_stack_health_dashboard(lgtm_endpoints: dict[str, str]) -> None:
    res = requests.get(
        f"{lgtm_endpoints['grafana']}/api/search",
        params={"query": "Stack health"},
        auth=("admin", "admin"),
        timeout=30,
    )
    res.raise_for_status()
    titles = {entry.get("title") for entry in res.json()}
    assert "Stack health" in titles


@pytest.mark.functional
@pytest.mark.t("T-38")
def test_loki_retention_config_effective(lgtm_endpoints: dict[str, str]) -> None:
    res = requests.get(f"{lgtm_endpoints['loki']}/config", timeout=30)
    res.raise_for_status()
    text = res.text
    assert "retention_period" in text
    assert "720h" in text or "30d" in text
    assert "retention_enabled: true" in text.lower()


@pytest.mark.functional
@pytest.mark.t("T-38")
def test_tempo_block_retention_effective(lgtm_endpoints: dict[str, str]) -> None:
    res = requests.get(f"{lgtm_endpoints['tempo']}/status/config", timeout=30)
    res.raise_for_status()
    assert "block_retention: 720h" in res.text or "block_retention: '720h'" in res.text
