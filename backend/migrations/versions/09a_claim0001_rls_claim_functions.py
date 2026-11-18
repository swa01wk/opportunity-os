"""RLS claim functions for workflow dispatch and outbox relay (SPEC-09a, ADR-023)."""

from __future__ import annotations

import logging
import os
from collections.abc import Sequence
from pathlib import Path

from alembic import op
from dbos import DBOS
from m0_access import assume_migrator, execute_sql_script
from sqlalchemy import text

revision: str = "09a_claim0001"
down_revision: str | Sequence[str] | None = "04m0baseline0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_log = logging.getLogger("alembic.runtime.migration")


def _sql_path() -> Path:
    return Path(__file__).resolve().parents[1] / "sql" / "09a_claim_functions_up.sql"


def _dbos_migrate_url(url: str) -> str:
    if url.startswith("postgresql+psycopg://"):
        return "postgresql://" + url.removeprefix("postgresql+psycopg://")
    return url


def upgrade() -> None:
    conn = op.get_bind()
    assume_migrator(conn)
    execute_sql_script(conn, _sql_path().read_text(encoding="utf-8"))
    conn.execute(text("RESET ROLE"))
    migrate_url = os.environ["MIGRATE_DATABASE_URL"]
    DBOS.migrate(
        system_database_url=_dbos_migrate_url(migrate_url),
        schema="dbos",
        application_role="oos_worker",
    )
    _log.info('{"event":"migration.applied","revision":"%s","dbos":"migrate"}', revision)


def downgrade() -> None:
    conn = op.get_bind()
    assume_migrator(conn)
    conn.execute(text("DROP FUNCTION IF EXISTS app.claim_workflow_requests(int)"))
    conn.execute(text("DROP FUNCTION IF EXISTS app.claim_outbox_events(int)"))
    conn.execute(text("RESET ROLE"))
