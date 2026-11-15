"""T-38: LGTM image provisioning and Prometheus retention (SPEC-08 AC4 partial)."""

from __future__ import annotations

import os
from pathlib import Path

import pytest
import requests
from testcontainers.core.container import DockerContainer
from wait_http import wait_http_ready


def _checkout_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _docker_mount_root() -> Path:
    return Path(os.environ.get("OOS_HOST_REPO", _checkout_root()))


def _lgtm_image(root: Path) -> str:
    for line in (_checkout_root() / "infra/images.env").read_text().splitlines():
        if line.startswith("LGTM_IMAGE="):
            return line.split("=", 1)[1].strip()
    msg = "LGTM_IMAGE missing from infra/images.env"
    raise RuntimeError(msg)


def _lgtm_container() -> DockerContainer:
    mount_root = _docker_mount_root()
    return (
        DockerContainer(_lgtm_image(_checkout_root()))
        .with_exposed_ports(3000, 9090)
        .with_env("PROMETHEUS_EXTRA_ARGS", "--storage.tsdb.retention.time=90d")
        .with_env(
            "LOKI_EXTRA_ARGS",
            (
                "-store.retention=30d -compactor.retention-enabled=true "
                "-compactor.delete-request-store=filesystem"
            ),
        )
        .with_volume_mapping(
            mount_root / "infra/grafana/lgtm/tempo-config.yaml",
            "/otel-lgtm/tempo-config.yaml",
        )
        .with_volume_mapping(
            mount_root / "infra/grafana/provisioning/dashboards/custom.yaml",
            "/otel-lgtm/grafana/conf/provisioning/dashboards/custom.yaml",
        )
        .with_volume_mapping(
            mount_root / "infra/grafana/dashboards/stack-health.json",
            "/otel-lgtm/grafana/conf/provisioning/dashboards/custom/stack-health.json",
        )
    )


@pytest.fixture(scope="module")
def lgtm_endpoints() -> dict[str, str]:
    container = _lgtm_container()
    container.start()
    host = container.get_container_host_ip()
    grafana_port = container.get_exposed_port(3000)
    prom_port = container.get_exposed_port(9090)
    wait_http_ready(f"http://{host}:{grafana_port}/api/health")
    endpoints = {
        "grafana": f"http://{host}:{grafana_port}",
        "prometheus": f"http://{host}:{prom_port}",
    }
    yield endpoints
    container.stop()


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
def test_prometheus_retention_flag_is_90d(lgtm_endpoints: dict[str, str]) -> None:
    import time

    stop = time.monotonic() + 60
    retention = ""
    while time.monotonic() < stop:
        try:
            res = requests.get(f"{lgtm_endpoints['prometheus']}/api/v1/status/flags", timeout=5)
            res.raise_for_status()
            retention = res.json()["data"]["storage.tsdb.retention.time"]
            if retention == "90d":
                break
        except requests.RequestException:
            pass
        time.sleep(0.25)
    assert retention == "90d"
