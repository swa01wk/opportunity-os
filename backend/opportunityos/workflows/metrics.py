"""Worker metrics for dispatch and outbox relay (SPEC-09a, OBSERVABILITY.md)."""

from __future__ import annotations

from opentelemetry import metrics
from opentelemetry.metrics import Observation

_METER = metrics.get_meter("opportunityos.worker")
_REGISTERED = False
_outbox_lag_seconds = 0.0


def set_outbox_lag_seconds(value: float) -> None:
    global _outbox_lag_seconds
    _outbox_lag_seconds = max(0.0, value)


def _observe_outbox_lag(_: object) -> list[Observation]:
    return [Observation(_outbox_lag_seconds)]


DISPATCH_SECONDS = _METER.create_histogram("oos.workflow_request.dispatch_seconds")
RELAY_DELIVERED = _METER.create_counter("oos.relay.delivered")


def register_worker_metrics() -> None:
    global _REGISTERED
    if _REGISTERED:
        return
    _METER.create_observable_gauge(
        "oos.outbox.lag_seconds",
        callbacks=[_observe_outbox_lag],
        description="Age in seconds of the oldest undelivered outbox event",
    )
    _REGISTERED = True
