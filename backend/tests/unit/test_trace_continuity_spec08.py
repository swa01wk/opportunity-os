"""T-38: traceparent continues from caller into api spans (SPEC-08 AC1 partial)."""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

from opportunityos.telemetry.log import configure_logging
from opportunityos.telemetry.otel import instrument_fastapi


@pytest.mark.t("T-38")
def test_api_span_shares_browser_trace_id(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OTEL_SDK_DISABLED", raising=False)
    exporter = InMemorySpanExporter()
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    app = FastAPI()
    app.add_api_route("/probe", lambda: {"ok": True}, methods=["GET"])
    configure_logging()
    instrument_fastapi(app, service_name="api-test", tracer_provider=provider)
    traceparent = "00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01"
    TestClient(app).get("/probe", headers={"traceparent": traceparent})
    trace_ids = {format(span.context.trace_id, "032x") for span in exporter.get_finished_spans()}
    assert "4bf92f3577b34da6a3ce929d0e0e4736" in trace_ids
