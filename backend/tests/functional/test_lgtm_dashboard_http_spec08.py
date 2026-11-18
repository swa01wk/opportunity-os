"""T-38: Stack health HTTP metrics from traced FastAPI via collector (SPEC-08 R2)."""

from __future__ import annotations

import json
import os
import time
from pathlib import Path

import pytest
import requests
from fastapi import FastAPI
from fastapi.testclient import TestClient
from lgtm_compose import lgtm_service_spec, mount_configured_volumes
from opentelemetry import metrics, trace
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from testcontainers.core.container import DockerContainer
from testcontainers.core.network import Network
from wait_http import wait_http_ready

from opportunityos.telemetry.service_up import register_service_up


def _checkout_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _docker_mount_root() -> Path:
    return Path(os.environ.get("OOS_HOST_REPO", _checkout_root()))


def _image_env(key: str) -> str:
    for line in (_checkout_root() / "infra/images.env").read_text().splitlines():
        if line.startswith(f"{key}="):
            return line.split("=", 1)[1].strip()
    raise RuntimeError(f"{key} missing from infra/images.env")


def _dashboard_exprs() -> list[str]:
    dashboard = json.loads(
        (_checkout_root() / "infra/grafana/dashboards/stack-health.json").read_text(),
    )
    return [
        target["expr"]
        for panel in dashboard["panels"]
        for target in panel.get("targets", [])
        if "expr" in target
    ]


def _wire_fastapi_to_collector(app: FastAPI, *, endpoint: str) -> None:
    resource = Resource.create({"service.name": "api"})
    tracer_provider = TracerProvider(resource=resource)
    tracer_provider.add_span_processor(
        BatchSpanProcessor(OTLPSpanExporter(endpoint=f"{endpoint}/v1/traces"))
    )
    trace.set_tracer_provider(tracer_provider)
    reader = PeriodicExportingMetricReader(
        OTLPMetricExporter(endpoint=f"{endpoint}/v1/metrics"),
        export_interval_millis=500,
    )
    metrics.set_meter_provider(MeterProvider(resource=resource, metric_readers=[reader]))
    register_service_up()
    FastAPIInstrumentor.instrument_app(
        app,
        tracer_provider=tracer_provider,
        excluded_urls="healthz,readyz",
    )


@pytest.fixture(scope="module")
def prometheus_url() -> str:
    os.environ["OTEL_SDK_DISABLED"] = "false"
    os.environ["OTEL_SEMCONV_STABILITY_OPT_IN"] = "http"
    compose = lgtm_service_spec(_checkout_root())
    mount_root = _docker_mount_root()
    network = Network()
    net_id = network.create()
    lgtm = (
        DockerContainer(_image_env("LGTM_IMAGE")).with_network(net_id).with_network_aliases("lgtm")
    )
    lgtm = lgtm.with_exposed_ports(3000, 9090)
    for key, value in compose["environment"].items():
        lgtm = lgtm.with_env(key, value)
    lgtm = mount_configured_volumes(lgtm, mount_root=mount_root, spec=compose)
    collector = (
        DockerContainer(_image_env("OTEL_COLLECTOR_IMAGE"))
        .with_network(net_id)
        .with_exposed_ports(4318, 13133)
        .with_volume_mapping(
            mount_root / "infra/otel-collector/config.yaml",
            "/etc/otelcol-contrib/config.yaml",
        )
        .with_command(["--config=/etc/otelcol-contrib/config.yaml"])
    )
    prom_url = ""
    try:
        lgtm.start()
        collector.start()
        lhost = lgtm.get_container_host_ip()
        wait_http_ready(f"http://{lhost}:{lgtm.get_exposed_port(3000)}/api/health")
        chost = collector.get_container_host_ip()
        wait_http_ready(f"http://{chost}:{collector.get_exposed_port(13133)}/")
        otlp = f"http://{chost}:{collector.get_exposed_port(4318)}"
        from fastapi import HTTPException

        app = FastAPI()

        @app.get("/probe")
        def probe() -> dict[str, str]:
            return {"ok": "true"}

        @app.get("/fail")
        def fail() -> None:
            raise HTTPException(status_code=500)

        _wire_fastapi_to_collector(app, endpoint=otlp)
        client = TestClient(app)
        for _ in range(12):
            client.get("/probe")
        client.get("/fail")
        meter_provider = metrics.get_meter_provider()
        meter_provider.force_flush()  # type: ignore[union-attr]
        prom_url = f"http://{lhost}:{lgtm.get_exposed_port(9090)}"
        yield prom_url
    finally:
        mp = metrics.get_meter_provider()
        if hasattr(mp, "shutdown"):
            mp.shutdown()
        tp = trace.get_tracer_provider()
        if hasattr(tp, "shutdown"):
            tp.shutdown()
        collector.stop()
        lgtm.stop()
        network.remove()


def _prometheus_has_data(prometheus_url: str, expr: str) -> bool:
    res = requests.get(
        f"{prometheus_url}/api/v1/query",
        params={"query": expr},
        timeout=10,
    )
    res.raise_for_status()
    return bool(res.json()["data"]["result"])


@pytest.mark.functional
@pytest.mark.t("T-38")
def test_stack_health_dashboard_exprs_return_data(prometheus_url: str) -> None:
    exprs = _dashboard_exprs()
    assert exprs, "dashboard has no Prometheus expressions"
    stop = time.monotonic() + 90
    missing: list[str] = []
    while time.monotonic() < stop:
        missing = [expr for expr in exprs if not _prometheus_has_data(prometheus_url, expr)]
        if not missing:
            return
        time.sleep(0.25)
    pytest.fail(f"Prometheus returned no series for: {missing}")
