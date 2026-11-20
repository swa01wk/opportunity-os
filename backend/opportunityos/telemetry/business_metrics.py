"""Cross-cutting business counters (SPEC-09a)."""

from __future__ import annotations

from opentelemetry import metrics

_METER = metrics.get_meter("opportunityos")
IDEMPOTENCY_REPLAYS = _METER.create_counter("oos.idempotency.replays")


def record_idempotency_replay() -> None:
    IDEMPOTENCY_REPLAYS.add(1)
