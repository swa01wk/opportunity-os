"""M0 baseline roles, RLS and grants (SPEC-04). Used by the Alembic revision only."""

from __future__ import annotations

import os
import re
from collections.abc import Iterable
from pathlib import Path
from typing import Literal

from psycopg import sql
from sqlalchemy import text
from sqlalchemy.engine import Connection

Privilege = Literal["SELECT", "INSERT", "UPDATE", "DELETE"]

LOGIN_ROLES = (
    "oos_api",
    "oos_worker",
    "oos_render",
    "oos_retention",
    "oos_analytics_ro",
)

ENV_PASSWORD_KEYS: dict[str, str] = {
    "oos_api": "DB_PASSWORD_API",
    "oos_worker": "DB_PASSWORD_WORKER",
    "oos_render": "DB_PASSWORD_RENDER",
    "oos_retention": "DB_PASSWORD_RETENTION",
    "oos_analytics_ro": "DB_PASSWORD_ANALYTICS_RO",
}

WORKSPACE_ID_TABLES: tuple[tuple[str, str], ...] = (
    ("app", "member"),
    ("app", "brand_kit"),
    ("app", "brand_kit_version"),
    ("app", "project"),
    ("app", "workflow_request"),
    ("app", "execution_run"),
    ("app", "task_attempt"),
    ("app", "outbox_event"),
    ("app", "audit_log"),
    ("app", "idempotency_key"),
    ("media", "render_job"),
)

M0_APP_TABLES: tuple[tuple[str, str], ...] = (
    ("app", "workspace"),
    ("app", "member"),
    ("app", "service_identity"),
    ("app", "brand_kit"),
    ("app", "brand_kit_version"),
    ("app", "project"),
    ("app", "workflow_request"),
    ("app", "execution_run"),
    ("app", "task_attempt"),
    ("app", "outbox_event"),
    ("app", "audit_log"),
    ("app", "idempotency_key"),
)

M0_MEDIA_TABLES: tuple[tuple[str, str], ...] = (("media", "render_job"),)

ALL_M0_TABLES = M0_APP_TABLES + M0_MEDIA_TABLES

# Domain tables api/worker may change; neither deletes (SECURITY.md:152).
_APP_MUTABLE: tuple[tuple[str, str], ...] = (
    ("app", "workspace"),
    ("app", "member"),
    ("app", "brand_kit"),
    ("app", "project"),
    ("app", "workflow_request"),
    ("app", "execution_run"),
    ("app", "task_attempt"),
    ("app", "outbox_event"),
    ("app", "idempotency_key"),
)

GrantRow = tuple[str, str, str, frozenset[Privilege]]


def _row(role: str, schema: str, table: str, privs: Iterable[Privilege]) -> GrantRow:
    return (role, schema, table, frozenset(privs))


def grant_matrix() -> tuple[GrantRow, ...]:
    """Explicit privileges per role and table (SECURITY.md least privilege)."""
    rows: list[GrantRow] = []

    for schema, table in _APP_MUTABLE:
        rows.append(_row("oos_api", schema, table, ("SELECT", "INSERT", "UPDATE")))
        rows.append(_row("oos_worker", schema, table, ("SELECT", "INSERT", "UPDATE")))
        rows.append(_row("oos_retention", schema, table, ("SELECT", "DELETE")))

    for role in ("oos_api", "oos_worker"):
        rows.append(_row(role, "app", "brand_kit_version", ("SELECT", "INSERT")))
        rows.append(_row(role, "app", "audit_log", ("SELECT", "INSERT")))

    rows.append(_row("oos_retention", "app", "brand_kit_version", ("SELECT",)))
    rows.append(_row("oos_retention", "app", "audit_log", ("SELECT",)))

    for role in ("oos_api", "oos_worker", "oos_retention"):
        rows.append(_row(role, "app", "service_identity", ("SELECT",)))

    rows.append(_row("oos_render", "media", "render_job", ("SELECT", "INSERT", "UPDATE", "DELETE")))
    rows.append(_row("oos_retention", "media", "render_job", ("SELECT", "DELETE")))

    return tuple(rows)


_MATRIX_INDEX: dict[tuple[str, str, str], frozenset[Privilege]] | None = None


def _matrix_index() -> dict[tuple[str, str, str], frozenset[Privilege]]:
    global _MATRIX_INDEX
    if _MATRIX_INDEX is None:
        idx: dict[tuple[str, str, str], frozenset[Privilege]] = {}
        for role, schema, table, privs in grant_matrix():
            idx[(role, schema, table)] = privs
        _MATRIX_INDEX = idx
    return _MATRIX_INDEX


def privileges_for(role: str, schema: str, table: str) -> frozenset[Privilege]:
    return _matrix_index().get((role, schema, table), frozenset())


def table_qualified_name(schema: str, table: str) -> str:
    return f"{schema}.{table}"


def sql_m0_tables() -> str:
    path = Path(__file__).resolve().parent / "sql" / "m0_tables_up.sql"
    return path.read_text(encoding="utf-8")


def execute_sql_script(conn: Connection, script: str) -> None:
    conn.exec_driver_sql(script)


def _validate_ident(name: str) -> None:
    if not re.fullmatch(r"[a-z_][a-z0-9_]*", name):
        msg = f"invalid SQL identifier: {name!r}"
        raise ValueError(msg)


def _validate_db_name(name: str) -> None:
    if not re.fullmatch(r"[a-zA-Z_][a-zA-Z0-9_]*", name):
        msg = f"unsupported database name: {name!r}"
        raise ValueError(msg)


def _run_composable(conn: Connection, statement: sql.Composable) -> None:
    conn.connection.driver_connection.execute(statement)


def _grant_table(
    conn: Connection,
    role: str,
    schema: str,
    table: str,
    privs: frozenset[Privilege],
) -> None:
    if not privs:
        return
    priv_sql = sql.SQL(", ").join(sql.SQL(p) for p in sorted(privs))
    _run_composable(
        conn,
        sql.SQL("GRANT {} ON TABLE {}.{} TO {}").format(
            priv_sql,
            sql.Identifier(schema),
            sql.Identifier(table),
            sql.Identifier(role),
        ),
    )


def create_roles(conn: Connection) -> None:
    conn.execute(text("CREATE ROLE oos_migrator NOLOGIN"))
    bootstrap = conn.execute(text("SELECT current_user AS name")).scalar_one()
    _validate_ident(bootstrap)
    _run_composable(
        conn,
        sql.SQL("GRANT {} TO {}").format(sql.Identifier("oos_migrator"), sql.Identifier(bootstrap)),
    )

    db_name = conn.execute(text("SELECT current_database()")).scalar_one()
    _validate_db_name(db_name)
    _run_composable(
        conn,
        sql.SQL("GRANT CREATE ON DATABASE {} TO {}").format(
            sql.Identifier(db_name),
            sql.Identifier("oos_migrator"),
        ),
    )

    for role in LOGIN_ROLES:
        env_key = ENV_PASSWORD_KEYS[role]
        password = os.environ.get(env_key)
        if not password:
            msg = f"missing {env_key} for role {role}"
            raise RuntimeError(msg)
        _run_composable(conn, sql.SQL("CREATE ROLE {} LOGIN").format(sql.Identifier(role)))
        conn.execute(text("SELECT set_config('oos.pw', :pw, true)"), {"pw": password})
        conn.execute(text("SELECT set_config('oos.role', :role, true)"), {"role": role})
        conn.execute(
            text(
                """
                DO $do$
                BEGIN
                  EXECUTE format(
                    'ALTER ROLE %I PASSWORD %L',
                    current_setting('oos.role'),
                    current_setting('oos.pw')
                  );
                END
                $do$;
                """
            )
        )
        _run_composable(
            conn,
            sql.SQL("GRANT {} TO {}").format(sql.Identifier(role), sql.Identifier(bootstrap)),
        )
        _run_composable(
            conn,
            sql.SQL("GRANT CONNECT ON DATABASE {} TO {}").format(
                sql.Identifier(db_name),
                sql.Identifier(role),
            ),
        )


def drop_roles(conn: Connection) -> None:
    bootstrap = conn.execute(text("SELECT current_user AS name")).scalar_one()
    _validate_ident(bootstrap)
    for role in (*reversed(LOGIN_ROLES), "oos_migrator"):
        _run_composable(
            conn,
            sql.SQL("DROP OWNED BY {} CASCADE").format(sql.Identifier(role)),
        )
    for role in reversed(LOGIN_ROLES):
        _run_composable(
            conn,
            sql.SQL("REVOKE {} FROM {}").format(sql.Identifier(role), sql.Identifier(bootstrap)),
        )
        _run_composable(conn, sql.SQL("DROP ROLE IF EXISTS {}").format(sql.Identifier(role)))
    _run_composable(
        conn,
        sql.SQL("REVOKE {} FROM {}").format(
            sql.Identifier("oos_migrator"),
            sql.Identifier(bootstrap),
        ),
    )
    conn.execute(text("DROP ROLE IF EXISTS oos_migrator"))


def assume_migrator(conn: Connection) -> None:
    conn.execute(text("SET LOCAL ROLE oos_migrator"))


def configure_ownership(conn: Connection) -> None:
    for schema in ("app", "media", "analytics", "dbos"):
        _run_composable(
            conn,
            sql.SQL("ALTER SCHEMA {} OWNER TO {}").format(
                sql.Identifier(schema),
                sql.Identifier("oos_migrator"),
            ),
        )
    for schema, table in ALL_M0_TABLES:
        _run_composable(
            conn,
            sql.SQL("ALTER TABLE {}.{} OWNER TO {}").format(
                sql.Identifier(schema),
                sql.Identifier(table),
                sql.Identifier("oos_migrator"),
            ),
        )


def apply_rls(conn: Connection) -> None:
    conn.execute(
        text(
            """
            ALTER TABLE app.workspace ENABLE ROW LEVEL SECURITY;
            ALTER TABLE app.workspace FORCE ROW LEVEL SECURITY;
            DROP POLICY IF EXISTS workspace_isolation ON app.workspace;
            CREATE POLICY workspace_isolation ON app.workspace
              USING (
                id = NULLIF(current_setting('app.workspace_id', true), '')::uuid
              );
            """
        )
    )
    for schema, table in WORKSPACE_ID_TABLES:
        _validate_ident(schema)
        _validate_ident(table)
        qualified = table_qualified_name(schema, table)
        conn.execute(
            text(
                f"""
                ALTER TABLE {qualified} ENABLE ROW LEVEL SECURITY;
                ALTER TABLE {qualified} FORCE ROW LEVEL SECURITY;
                DROP POLICY IF EXISTS workspace_isolation ON {qualified};
                CREATE POLICY workspace_isolation ON {qualified}
                  USING (
                    workspace_id = NULLIF(
                      current_setting('app.workspace_id', true), ''
                    )::uuid
                  );
                """
            )
        )


def drop_rls(conn: Connection) -> None:
    conn.execute(text("DROP POLICY IF EXISTS workspace_isolation ON app.workspace"))
    conn.execute(text("ALTER TABLE app.workspace NO FORCE ROW LEVEL SECURITY"))
    conn.execute(text("ALTER TABLE app.workspace DISABLE ROW LEVEL SECURITY"))
    for schema, table in WORKSPACE_ID_TABLES:
        qualified = table_qualified_name(schema, table)
        conn.execute(text(f"DROP POLICY IF EXISTS workspace_isolation ON {qualified}"))
        conn.execute(text(f"ALTER TABLE {qualified} NO FORCE ROW LEVEL SECURITY"))
        conn.execute(text(f"ALTER TABLE {qualified} DISABLE ROW LEVEL SECURITY"))


def apply_grants(conn: Connection) -> None:
    schema_roles: tuple[tuple[str, tuple[str, ...]], ...] = (
        ("app", ("oos_api", "oos_worker", "oos_retention")),
        ("media", ("oos_render", "oos_retention")),
        ("analytics", ("oos_analytics_ro",)),
        ("dbos", ("oos_worker",)),
    )
    for schema, roles in schema_roles:
        for role in roles:
            _run_composable(
                conn,
                sql.SQL("GRANT USAGE ON SCHEMA {} TO {}").format(
                    sql.Identifier(schema),
                    sql.Identifier(role),
                ),
            )

    for role, schema, table, privs in grant_matrix():
        _grant_table(conn, role, schema, table, privs)

    for role in ("oos_api", "oos_worker"):
        _run_composable(
            conn,
            sql.SQL("GRANT USAGE, SELECT ON SEQUENCE {}.{} TO {}").format(
                sql.Identifier("app"),
                sql.Identifier("audit_log_id_seq"),
                sql.Identifier(role),
            ),
        )
        _run_composable(
            conn,
            sql.SQL("GRANT USAGE, SELECT ON SEQUENCE {}.{} TO {}").format(
                sql.Identifier("app"),
                sql.Identifier("outbox_event_seq_seq"),
                sql.Identifier(role),
            ),
        )

    _run_composable(
        conn,
        sql.SQL("GRANT CREATE ON SCHEMA {} TO {}").format(
            sql.Identifier("dbos"),
            sql.Identifier("oos_worker"),
        ),
    )
    conn.execute(
        text(
            """
            ALTER DEFAULT PRIVILEGES FOR ROLE oos_migrator IN SCHEMA dbos
              GRANT ALL ON TABLES TO oos_worker
            """
        )
    )
    conn.execute(
        text(
            """
            ALTER DEFAULT PRIVILEGES FOR ROLE oos_migrator IN SCHEMA dbos
              GRANT ALL ON SEQUENCES TO oos_worker
            """
        )
    )


def drop_m0_schema(conn: Connection) -> None:
    for schema, table in reversed(ALL_M0_TABLES):
        _run_composable(
            conn,
            sql.SQL("DROP TABLE IF EXISTS {}.{} CASCADE").format(
                sql.Identifier(schema),
                sql.Identifier(table),
            ),
        )
    for schema in reversed(("analytics", "media", "app", "dbos")):
        _run_composable(
            conn,
            sql.SQL("DROP SCHEMA IF EXISTS {} CASCADE").format(sql.Identifier(schema)),
        )
