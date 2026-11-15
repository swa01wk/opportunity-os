"""T-38: traceparent propagation helpers (SPEC-08)."""

import pytest
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

from opportunityos.telemetry.propagation import current_traceparent, inject_traceparent


@pytest.mark.t("T-38")
def test_traceparent_round_trip(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OTEL_SDK_DISABLED", raising=False)
    provider = TracerProvider(resource=Resource.create({"service.name": "test"}))
    provider.add_span_processor(SimpleSpanProcessor(InMemorySpanExporter()))
    trace.set_tracer_provider(provider)
    tracer = trace.get_tracer("test")
    with tracer.start_as_current_span("api.health"):
        carrier: dict[str, str] = {}
        inject_traceparent(carrier)
        parent = current_traceparent()
        assert parent is not None
        injected = carrier.get("traceparent")
        assert injected is not None
        assert injected.split("-")[1] == parent.split("-")[1]
        assert injected.split("-")[2] == parent.split("-")[2]
