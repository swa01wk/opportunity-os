"""Observable gauge proving the process is exporting telemetry (SPEC-08, OBSERVABILITY.md)."""

from __future__ import annotations

from opentelemetry import metrics
from opentelemetry.metrics import Observation

_REGISTERED = False


def register_service_up() -> None:
    global _REGISTERED
    if _REGISTERED:
        return

    def _observe(_: object) -> list[Observation]:
        return [Observation(1)]

    metrics.get_meter("opportunityos.service").create_observable_gauge(
        "oos.service.up",
        callbacks=[_observe],
        description="Set to 1 while the process exports OTLP metrics",
    )
    _REGISTERED = True
