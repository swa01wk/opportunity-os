"""RLS claim functions for workflow dispatch and outbox relay (SPEC-09a, ADR-023)."""

from __future__ import annotations

import logging
from collections.abc import Sequence
from pathlib import Path

from alembic import op
from m0_access import assume_migrator, execute_sql_script
from sqlalchemy import text

revision: str = "09a_claim0001"
down_revision: str | Sequence[str] | None = "04m0baseline0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_log = logging.getLogger("alembic.runtime.migration")


def _sql_path() -> Path:
    return Path(__file__).resolve().parents[1] / "sql" / "09a_claim_functions_up.sql"


def upgrade() -> None:
    conn = op.get_bind()
    assume_migrator(conn)
    execute_sql_script(conn, _sql_path().read_text(encoding="utf-8"))
    conn.execute(text("RESET ROLE"))
    _log.info('{"event":"migration.applied","revision":"%s"}', revision)


def downgrade() -> None:
    conn = op.get_bind()
    assume_migrator(conn)
    conn.execute(text("DROP FUNCTION IF EXISTS app.claim_workflow_requests(int)"))
    conn.execute(text("DROP FUNCTION IF EXISTS app.claim_outbox_events(int)"))
    conn.execute(text("DROP POLICY IF EXISTS claim_poll_select ON app.workflow_request"))
    conn.execute(text("DROP POLICY IF EXISTS claim_poll_update ON app.workflow_request"))
    conn.execute(text("DROP POLICY IF EXISTS claim_poll_select ON app.outbox_event"))
    conn.execute(text("DROP POLICY IF EXISTS claim_poll_update ON app.outbox_event"))
    conn.execute(text("RESET ROLE"))
