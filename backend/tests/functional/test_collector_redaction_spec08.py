"""T-38: Collector redaction and span allowlist with logger redaction off (SPEC-08 AC2-AC3)."""

from __future__ import annotations

import os
import time
from pathlib import Path

import pytest
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from testcontainers.core.container import DockerContainer

COLLECTOR_IMAGE = "otel/opentelemetry-collector-contrib:0.151.0"
NOT_ALLOWED = "oos.disallowed_attribute"


def _repo_root() -> Path:
    return Path(os.environ.get("OOS_HOST_REPO", Path(__file__).resolve().parents[3]))


def _collector_container() -> DockerContainer:
    root = _repo_root()
    return (
        DockerContainer(COLLECTOR_IMAGE)
        .with_exposed_ports(4318)
        .with_volume_mapping(
            root / "infra/otel-collector/config.functional-test.yaml",
            "/etc/otelcol-contrib/config.yaml",
        )
    )


@pytest.fixture(scope="module")
def collector_export() -> str:
    with _collector_container() as container:
        container.start()
        time.sleep(3)
        host = container.get_container_host_ip()
        port = container.get_exposed_port(4318)
        endpoint = f"http://{host}:{port}"
        resource = Resource.create({"service.name": "t38-collector-test"})
        provider = TracerProvider(resource=resource)
        provider.add_span_processor(
            SimpleSpanProcessor(OTLPSpanExporter(endpoint=f"{endpoint}/v1/traces"))
        )
        trace.set_tracer_provider(provider)
        tracer = trace.get_tracer("t38")
        with tracer.start_as_current_span(
            "t38.redaction",
            attributes={
                "http.route": "/synthetic",
                "authorization": "Bearer leaked",
                "contact_email": "leak@example.com",
                NOT_ALLOWED: "drop-me",
                "http.url": "https://store/bucket?X-Amz-Signature=abc123",
            },
        ):
            pass
        provider.force_flush()
        time.sleep(2)
        return container.get_logs()


@pytest.mark.functional
@pytest.mark.t("T-38")
def test_collector_redacts_sensitive_span_fields(collector_export: str) -> None:
    assert "leak@example.com" not in collector_export
    assert "Bearer leaked" not in collector_export
    assert "abc123" not in collector_export


@pytest.mark.functional
@pytest.mark.t("T-38")
def test_collector_drops_disallowed_span_attributes(collector_export: str) -> None:
    assert NOT_ALLOWED not in collector_export
