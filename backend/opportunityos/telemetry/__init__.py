"""OpenTelemetry and structlog wiring (SPEC-08, ADR-016)."""

from opportunityos.telemetry.log import (
    bind_request_id,
    configure_logging,
    get_logger,
    uvicorn_log_config,
)
from opportunityos.telemetry.otel import configure_otel, instrument_fastapi
from opportunityos.telemetry.propagation import current_traceparent, inject_traceparent
from opportunityos.telemetry.redaction import redact_event_dict

__all__ = [
    "bind_request_id",
    "configure_logging",
    "configure_otel",
    "current_traceparent",
    "get_logger",
    "inject_traceparent",
    "instrument_fastapi",
    "redact_event_dict",
    "uvicorn_log_config",
]
