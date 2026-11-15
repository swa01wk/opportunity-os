"""T-38: Collector redaction and span allowlist against config.yaml (SPEC-08 AC2-AC3)."""

from __future__ import annotations

import logging
import os
from pathlib import Path

import pytest
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import SimpleLogRecordProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from testcontainers.core.container import DockerContainer
from wait_http import wait_http_ready

NOT_ALLOWED = "oos.disallowed_attribute"
SECRET_ATTR = "client_secret"  # noqa: S105 — synthetic attribute name for T-38


def _checkout_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _docker_mount_root() -> Path:
    """Host path for bind mounts when pytest runs inside py-functional (repo at /repo)."""
    return Path(os.environ.get("OOS_HOST_REPO", _checkout_root()))


def _collector_image(root: Path) -> str:
    for line in (_checkout_root() / "infra/images.env").read_text().splitlines():
        if line.startswith("OTEL_COLLECTOR_IMAGE="):
            return line.split("=", 1)[1].strip()
    msg = "OTEL_COLLECTOR_IMAGE missing from infra/images.env"
    raise RuntimeError(msg)


def _collector_container() -> DockerContainer:
    mount_root = _docker_mount_root()
    return (
        DockerContainer(_collector_image(_checkout_root()))
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
def collector_output() -> str:
    resource = Resource.create({"service.name": "t38-collector-test"})
    with _collector_container() as container:
        container.start()
        host = container.get_container_host_ip()
        wait_http_ready(f"http://{host}:{container.get_exposed_port(13133)}/")
        port = container.get_exposed_port(4318)
        endpoint = f"http://{host}:{port}"
        tracer_provider = TracerProvider(resource=resource)
        tracer = tracer_provider.get_tracer("t38")
        tracer_provider.add_span_processor(
            SimpleSpanProcessor(OTLPSpanExporter(endpoint=f"{endpoint}/v1/traces"))
        )
        with tracer.start_as_current_span(
            "t38.redaction",
            attributes={
                "http.route": "/synthetic",
                "authorization": "Bearer leaked",
                "gen_ai.usage.input_tokens": 123,
                SECRET_ATTR: "top-secret",
                NOT_ALLOWED: "drop-me",
                "http.url": "https://store/bucket?X-Amz-Signature=abc123",
            },
        ):
            pass
        tracer_provider.force_flush()
        log_provider = LoggerProvider(resource=resource)
        log_provider.add_log_record_processor(
            SimpleLogRecordProcessor(OTLPLogExporter(endpoint=f"{endpoint}/v1/logs"))
        )
        otel_log = logging.getLogger("t38.collector")
        otel_log.handlers.clear()
        otel_log.addHandler(LoggingHandler(level=logging.INFO, logger_provider=log_provider))
        otel_log.info(
            "contact owner@example.com Authorization: Bearer leaked token ?X-Amz-Signature=abc123",
            extra={"client_secret": "top-secret"},
        )
        log_provider.force_flush()
        return container.get_wrapped_container().logs(stdout=True, stderr=True)


def _output_text(collector_output: str | bytes) -> str:
    if isinstance(collector_output, (bytes, bytearray)):
        return collector_output.decode(errors="replace")
    return str(collector_output)


@pytest.mark.functional
@pytest.mark.t("T-38")
def test_collector_redacts_sensitive_span_fields(collector_output: str) -> None:
    text = _output_text(collector_output)
    assert "owner@example.com" not in text
    assert "Bearer leaked" not in text
    assert "abc123" not in text
    assert "top-secret" not in text


@pytest.mark.functional
@pytest.mark.t("T-38")
def test_collector_drops_disallowed_span_attributes(collector_output: str) -> None:
    assert NOT_ALLOWED not in _output_text(collector_output)
