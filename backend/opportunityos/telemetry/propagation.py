"""W3C traceparent helpers for outbox payloads (SPEC-08; SPEC-09a consumes)."""

from __future__ import annotations

from collections.abc import MutableMapping

from opentelemetry import trace
from opentelemetry.propagate import inject
from opentelemetry.trace import format_trace_id

CORRELATION_KEYS = (
    "oos.workspace_id",
    "oos.project_id",
    "oos.run_id",
    "oos.task_attempt_id",
    "oos.workflow_type",
    "oos.task_type",
    "oos.gate",
    "oos.artifact_sha256",
    "oos.render_job_id",
)


def current_traceparent() -> str | None:
    span = trace.get_current_span()
    ctx = span.get_span_context()
    if not ctx.is_valid:
        return None
    trace_id = format_trace_id(ctx.trace_id)
    span_id = format(ctx.span_id, "016x")
    flags = "01" if ctx.trace_flags.sampled else "00"
    return f"00-{trace_id}-{span_id}-{flags}"


def inject_traceparent(carrier: MutableMapping[str, str]) -> None:
    inject(carrier)


def set_correlation_attributes(**attrs: str) -> None:
    span = trace.get_current_span()
    for key, value in attrs.items():
        if key in CORRELATION_KEYS and value:
            span.set_attribute(key, value)
