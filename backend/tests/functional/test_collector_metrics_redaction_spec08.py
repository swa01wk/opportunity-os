"""T-38: Collector redaction allowlist keeps stable HTTP metric attributes (SPEC-08 R2)."""

from __future__ import annotations

import os
import time
from pathlib import Path

import pytest
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from testcontainers.core.container import DockerContainer
from wait_http import wait_http_ready


def _checkout_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _docker_mount_root() -> Path:
    return Path(os.environ.get("OOS_HOST_REPO", _checkout_root()))


def _collector_image() -> str:
    for line in (_checkout_root() / "infra/images.env").read_text().splitlines():
        if line.startswith("OTEL_COLLECTOR_IMAGE="):
            return line.split("=", 1)[1].strip()
    raise RuntimeError("OTEL_COLLECTOR_IMAGE missing")


def _output_text(raw: str | bytes) -> str:
    if isinstance(raw, (bytes, bytearray)):
        return raw.decode(errors="replace")
    return str(raw)


def _collector_container() -> DockerContainer:
    mount_root = _docker_mount_root()
    return (
        DockerContainer(_collector_image())
        .with_exposed_ports(4318, 13133)
        .with_volume_mapping(
            mount_root / "infra/otel-collector/config.yaml",
            "/etc/otelcol-contrib/config.yaml",
        )
        .with_volume_mapping(
            mount_root / "infra/otel-collector/config.test-override.yaml",
            "/etc/otelcol-contrib/test-override.yaml",
        )
        .with_command(
            [
                "--config=/etc/otelcol-contrib/config.yaml",
                "--config=/etc/otelcol-contrib/test-override.yaml",
            ]
        )
    )


@pytest.fixture(scope="module")
def collector_metrics_output() -> str:
    resource = Resource.create({"service.name": "t38-metrics"})
    with _collector_container() as container:
        container.start()
        host = container.get_container_host_ip()
        wait_http_ready(f"http://{host}:{container.get_exposed_port(13133)}/")
        endpoint = f"http://{host}:{container.get_exposed_port(4318)}"
        reader = PeriodicExportingMetricReader(
            OTLPMetricExporter(endpoint=f"{endpoint}/v1/metrics"),
            export_interval_millis=200,
        )
        provider = MeterProvider(resource=resource, metric_readers=[reader])
        meter = provider.get_meter("t38.metrics")
        counter = meter.create_counter("t38.synthetic.http")
        counter.add(
            1,
            {
                "http.request.method": "GET",
                "http.response.status_code": 200,
                "network.protocol.version": "1.1",
                "url.scheme": "http",
                "authorization": "Bearer leaked",
            },
        )
        provider.force_flush()
        stop = time.monotonic() + 10
        text = ""
        while time.monotonic() < stop:
            text = _output_text(container.get_wrapped_container().logs(stdout=True, stderr=True))
            if "http.request.method" in text:
                break
            time.sleep(0.25)
        provider.shutdown()
        return text


@pytest.mark.functional
@pytest.mark.t("T-38")
def test_collector_metrics_keep_http_attributes(collector_metrics_output: str) -> None:
    text = _output_text(collector_metrics_output)
    assert "http.request.method" in text
    assert "http.response.status_code" in text
    assert "network.protocol.version" in text
    assert "url.scheme" in text
    assert "Bearer leaked" not in text
