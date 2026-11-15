"""T-38: traceparent continues from caller into api spans (SPEC-08 AC1 partial)."""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter


@pytest.mark.t("T-38")
def test_api_span_shares_browser_trace_id(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OTEL_SDK_DISABLED", raising=False)
    exporter = InMemorySpanExporter()
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    trace.set_tracer_provider(provider)
    app = FastAPI()
    app.add_api_route("/probe", lambda: {"ok": True}, methods=["GET"])
    FastAPIInstrumentor.instrument_app(app, excluded_urls="healthz,readyz")
    traceparent = "00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01"
    TestClient(app).get("/probe", headers={"traceparent": traceparent})
    trace_ids = {format(span.context.trace_id, "032x") for span in exporter.get_finished_spans()}
    assert "4bf92f3577b34da6a3ce929d0e0e4736" in trace_ids
