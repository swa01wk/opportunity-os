"""M0 database baseline: schemas, tables, service roles, RLS (SPEC-04)."""

from __future__ import annotations

import logging
from collections.abc import Sequence

from alembic import op
from m0_access import (
    apply_grants,
    apply_rls,
    assume_migrator,
    configure_ownership,
    create_roles,
    drop_m0_schema,
    drop_rls,
    drop_roles,
    execute_sql_script,
    sql_m0_tables,
)
from sqlalchemy import text

revision: str = "04m0baseline0001"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_log = logging.getLogger("alembic.runtime.migration")


def upgrade() -> None:
    conn = op.get_bind()
    create_roles(conn)
    assume_migrator(conn)
    execute_sql_script(conn, sql_m0_tables())
    configure_ownership(conn)
    apply_rls(conn)
    apply_grants(conn)
    conn.execute(text("RESET ROLE"))
    _log.info(
        '{"event":"migration.applied","revision":"%s"}',
        revision,
    )


def downgrade() -> None:
    conn = op.get_bind()
    assume_migrator(conn)
    drop_rls(conn)
    drop_m0_schema(conn)
    conn.execute(text("RESET ROLE"))
    drop_roles(conn)
