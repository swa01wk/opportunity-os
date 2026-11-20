"""Outbox relay skeleton with pluggable sinks (SPEC-09a; SPEC-10 adds AG-UI)."""

from __future__ import annotations

import json
from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any

import structlog
from opentelemetry import trace
from sqlalchemy import text
from sqlalchemy.engine import Engine

from opportunityos.workflows.claim import claim_outbox_events
from opportunityos.workflows.metrics import RELAY_DELIVERED, set_outbox_lag_seconds

_log = structlog.get_logger(__name__)
_TRACER = trace.get_tracer(__name__)

OutboxSink = Callable[[dict[str, Any]], None]


def relay_batch(
    engine: Engine,
    *,
    sinks: tuple[OutboxSink, ...] = (),
    limit: int = 32,
) -> int:
    """Deliver outbox events in ``seq`` order; stop at the first sink failure."""
    delivered = 0
    with engine.connect() as conn, conn.begin():
        conn.execute(text("SET LOCAL ROLE oos_worker"))
        conn.execute(text("SELECT set_config('app.claim_bypass', '1', true)"))
        claimed = claim_outbox_events(conn, limit=limit)
        for row in claimed:
            nested = conn.begin_nested()
            try:
                with _TRACER.start_as_current_span("relay.deliver"):
                    conn.execute(
                        text("SELECT set_config('app.workspace_id', :wid, true)"),
                        {"wid": str(row.workspace_id)},
                    )
                    event_row = (
                        conn.execute(
                            text(
                                """
                                SELECT type, body, seq, created_at
                                FROM app.outbox_event
                                WHERE id = :id
                                """
                            ),
                            {"id": str(row.row_id)},
                        )
                        .mappings()
                        .one()
                    )
                    body: Any = event_row["body"]
                    if isinstance(body, str):
                        body = json.loads(body)
                    created_at = event_row["created_at"]
                    lag = (datetime.now(tz=UTC) - created_at).total_seconds()
                    set_outbox_lag_seconds(max(0.0, lag))
                    payload = {"type": event_row["type"], "body": body, "seq": event_row["seq"]}
                    for sink in sinks:
                        sink(payload)
                    conn.execute(
                        text(
                            """
                            UPDATE app.outbox_event
                            SET delivered_at = :ts
                            WHERE id = :id AND delivered_at IS NULL
                            """
                        ),
                        {"id": str(row.row_id), "ts": datetime.now(tz=UTC)},
                    )
                    RELAY_DELIVERED.add(1)
                    delivered += 1
            except Exception:
                nested.rollback()
                _log.warning("relay.retry", event_id=str(row.row_id))
                break
    return delivered


def relay_once(engine: Engine, *, sinks: tuple[OutboxSink, ...] = (), limit: int = 32) -> int:
    return relay_batch(engine, sinks=sinks, limit=limit)
