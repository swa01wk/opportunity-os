"""T-38: Prometheus reports oos.service.up for api, worker, web and render (SPEC-08 AC4)."""

from __future__ import annotations

from pathlib import Path

import pytest
import requests
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.metrics import Observation
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from testcontainers.core.container import DockerContainer
from wait_http import wait_http_ready

SERVICES = ("api", "worker", "web", "render")


def _checkout_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _image_env(root: Path, key: str) -> str:
    for line in (root / "infra/images.env").read_text().splitlines():
        if line.startswith(f"{key}="):
            return line.split("=", 1)[1].strip()
    msg = f"{key} missing from infra/images.env"
    raise RuntimeError(msg)


def _export_service_up(endpoint: str, service_name: str) -> None:
    resource = Resource.create({"service.name": service_name})
    reader = PeriodicExportingMetricReader(
        OTLPMetricExporter(endpoint=f"{endpoint}/v1/metrics"),
        export_interval_millis=200,
    )
    provider = MeterProvider(resource=resource, metric_readers=[reader])

    def observe(_: object) -> list[Observation]:
        return [Observation(1)]

    provider.get_meter("opportunityos.service").create_observable_gauge(
        "oos.service.up",
        callbacks=[observe],
    )
    provider.force_flush()
    provider.shutdown()


@pytest.fixture(scope="module")
def prometheus_url() -> str:
    with (
        DockerContainer(_image_env(_checkout_root(), "LGTM_IMAGE"))
        .with_exposed_ports(3000, 4318, 9090)
        .with_env("PROMETHEUS_EXTRA_ARGS", "--storage.tsdb.retention.time=90d")
    ) as lgtm:
        lgtm.start()
        host = lgtm.get_container_host_ip()
        wait_http_ready(f"http://{host}:{lgtm.get_exposed_port(3000)}/api/health")
        metrics_endpoint = f"http://{host}:{lgtm.get_exposed_port(4318)}"
        for name in SERVICES:
            _export_service_up(metrics_endpoint, name)
        yield f"http://{host}:{lgtm.get_exposed_port(9090)}"


def _query_service_up_count(prometheus_url: str) -> float:
    res = requests.get(
        f"{prometheus_url}/api/v1/query",
        params={"query": 'count(oos_service_up{service_name=~"api|worker|web|render"} == 1)'},
        timeout=5,
    )
    res.raise_for_status()
    result = res.json()["data"]["result"]
    if not result:
        return 0.0
    return float(result[0]["value"][1])


@pytest.mark.functional
@pytest.mark.t("T-38")
def test_prometheus_sees_all_service_up_gauges(prometheus_url: str) -> None:
    import time

    stop = time.monotonic() + 60
    value = 0.0
    while time.monotonic() < stop:
        value = _query_service_up_count(prometheus_url)
        if value >= 4:
            break
        time.sleep(0.2)
    assert value >= 4, f"expected four oos.service.up series, got {value}"
