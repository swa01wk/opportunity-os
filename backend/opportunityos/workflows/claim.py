"""Claim undelivered workflow and outbox rows via ADR-023 functions."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.engine import Connection


@dataclass(frozen=True, slots=True)
class ClaimedRow:
    row_id: UUID
    workspace_id: UUID


def claim_workflow_requests(conn: Connection, *, limit: int) -> list[ClaimedRow]:
    rows = conn.execute(
        text("SELECT id, workspace_id FROM app.claim_workflow_requests(:lim)"),
        {"lim": limit},
    ).all()
    claimed: list[ClaimedRow] = []
    for row in rows:
        claimed.append(
            ClaimedRow(row_id=UUID(str(row.id)), workspace_id=UUID(str(row.workspace_id))),
        )
    return claimed


def claim_outbox_events(conn: Connection, *, limit: int) -> list[ClaimedRow]:
    rows = conn.execute(
        text("SELECT id, workspace_id FROM app.claim_outbox_events(:lim)"),
        {"lim": limit},
    ).all()
    claimed: list[ClaimedRow] = []
    for row in rows:
        claimed.append(
            ClaimedRow(row_id=UUID(str(row.id)), workspace_id=UUID(str(row.workspace_id))),
        )
    return claimed
