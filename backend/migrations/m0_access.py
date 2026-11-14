"""M0 baseline roles, RLS and grants (SPEC-04). Used by the Alembic revision only."""

from __future__ import annotations

import os
import re
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.engine import Connection

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

VERSION_TABLES: tuple[tuple[str, str], ...] = (("app", "brand_kit_version"),)

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


def sql_m0_tables() -> str:
    path = Path(__file__).resolve().parent / "sql" / "m0_tables_up.sql"
    return path.read_text(encoding="utf-8")


def execute_sql_script(conn: Connection, script: str) -> None:
    for raw in script.split(";"):
        stmt = raw.strip()
        if stmt:
            conn.execute(text(stmt))


def _quote_password(raw: str) -> str:
    return raw.replace("'", "''")


def _pg_ident(name: str) -> str:
    if not re.fullmatch(r"[a-z_][a-z0-9_]*", name):
        msg = f"invalid SQL identifier: {name!r}"
        raise ValueError(msg)
    return name


def _qualified(schema: str, table: str) -> str:
    return f"{_pg_ident(schema)}.{_pg_ident(table)}"


def create_roles(conn: Connection) -> None:
    conn.execute(text("CREATE ROLE oos_migrator NOLOGIN"))
    bootstrap = conn.execute(text("SELECT current_user AS name")).one().name
    conn.execute(text(f"GRANT oos_migrator TO {_pg_ident(bootstrap)}"))
    db_name = conn.execute(text("SELECT current_database()")).scalar_one()
    if not re.fullmatch(r"[a-zA-Z_][a-zA-Z0-9_]*", db_name):
        msg = f"unsupported database name for grants: {db_name!r}"
        raise ValueError(msg)
    conn.execute(text(f"GRANT CREATE ON DATABASE {_pg_ident(db_name)} TO oos_migrator"))

    for role in LOGIN_ROLES:
        env_key = ENV_PASSWORD_KEYS[role]
        password = os.environ.get(env_key)
        if not password:
            msg = f"missing {env_key} for role {role}"
            raise RuntimeError(msg)
        conn.execute(
            text(f"CREATE ROLE {_pg_ident(role)} LOGIN PASSWORD '{_quote_password(password)}'")
        )
        conn.execute(text(f"GRANT {_pg_ident(role)} TO {_pg_ident(bootstrap)}"))

    for role in LOGIN_ROLES:
        conn.execute(text(f"GRANT CONNECT ON DATABASE {_pg_ident(db_name)} TO {_pg_ident(role)}"))


def drop_roles(conn: Connection) -> None:
    bootstrap = conn.execute(text("SELECT current_user AS name")).one().name
    for role in (*reversed(LOGIN_ROLES), "oos_migrator"):
        conn.execute(text(f"DROP OWNED BY {_pg_ident(role)} CASCADE"))
    for role in reversed(LOGIN_ROLES):
        conn.execute(text(f"REVOKE {_pg_ident(role)} FROM {_pg_ident(bootstrap)}"))
        conn.execute(text(f"DROP ROLE IF EXISTS {_pg_ident(role)}"))
    conn.execute(text(f"REVOKE oos_migrator FROM {_pg_ident(bootstrap)}"))
    conn.execute(text("DROP ROLE IF EXISTS oos_migrator"))


def assume_migrator(conn: Connection) -> None:
    conn.execute(text("SET LOCAL ROLE oos_migrator"))


def configure_ownership(conn: Connection) -> None:
    for schema in ("app", "media", "analytics", "dbos"):
        conn.execute(text(f"ALTER SCHEMA {_pg_ident(schema)} OWNER TO oos_migrator"))
    for schema, table in ALL_M0_TABLES:
        conn.execute(text(f"ALTER TABLE {_qualified(schema, table)} OWNER TO oos_migrator"))


def apply_rls(conn: Connection) -> None:
    conn.execute(
        text(
            """
            ALTER TABLE app.workspace ENABLE ROW LEVEL SECURITY;
            ALTER TABLE app.workspace FORCE ROW LEVEL SECURITY;
            DROP POLICY IF EXISTS workspace_isolation ON app.workspace;
            CREATE POLICY workspace_isolation ON app.workspace
              USING (id = current_setting('app.workspace_id', true)::uuid);
            """
        )
    )
    for schema, table in WORKSPACE_ID_TABLES:
        qualified = _qualified(schema, table)
        conn.execute(
            text(
                f"""
                ALTER TABLE {qualified} ENABLE ROW LEVEL SECURITY;
                ALTER TABLE {qualified} FORCE ROW LEVEL SECURITY;
                DROP POLICY IF EXISTS workspace_isolation ON {qualified};
                CREATE POLICY workspace_isolation ON {qualified}
                  USING (workspace_id = current_setting('app.workspace_id', true)::uuid);
                """
            )
        )


def drop_rls(conn: Connection) -> None:
    conn.execute(text("DROP POLICY IF EXISTS workspace_isolation ON app.workspace"))
    conn.execute(text("ALTER TABLE app.workspace NO FORCE ROW LEVEL SECURITY"))
    conn.execute(text("ALTER TABLE app.workspace DISABLE ROW LEVEL SECURITY"))
    for schema, table in WORKSPACE_ID_TABLES:
        qualified = _qualified(schema, table)
        conn.execute(text(f"DROP POLICY IF EXISTS workspace_isolation ON {qualified}"))
        conn.execute(text(f"ALTER TABLE {qualified} NO FORCE ROW LEVEL SECURITY"))
        conn.execute(text(f"ALTER TABLE {qualified} DISABLE ROW LEVEL SECURITY"))


def _grant_tables(
    conn: Connection,
    role: str,
    tables: tuple[tuple[str, str], ...],
    *,
    select: bool = False,
    insert: bool = False,
    update: bool = False,
    delete: bool = False,
) -> None:
    priv_parts = [
        p
        for flag, p in (
            (select, "SELECT"),
            (insert, "INSERT"),
            (update, "UPDATE"),
            (delete, "DELETE"),
        )
        if flag
    ]
    if not priv_parts:
        return
    priv = ", ".join(priv_parts)
    for schema, table in tables:
        qualified = _qualified(schema, table)
        target = _pg_ident(role)
        conn.execute(text(f"GRANT {priv} ON TABLE {qualified} TO {target}"))


def apply_grants(conn: Connection) -> None:
    for schema in ("app", "media", "analytics", "dbos"):
        conn.execute(text(f"GRANT USAGE ON SCHEMA {_pg_ident(schema)} TO PUBLIC"))

    app_mutable = tuple(
        t for t in M0_APP_TABLES if t not in VERSION_TABLES and t != ("app", "audit_log")
    )
    app_read = (*M0_APP_TABLES, ("media", "render_job"))

    for role in LOGIN_ROLES:
        conn.execute(text(f"GRANT USAGE ON SCHEMA app TO {_pg_ident(role)}"))
        conn.execute(text(f"GRANT USAGE ON SCHEMA media TO {_pg_ident(role)}"))
        conn.execute(text(f"GRANT USAGE ON SCHEMA analytics TO {_pg_ident(role)}"))
        conn.execute(text(f"GRANT USAGE ON SCHEMA dbos TO {_pg_ident(role)}"))

    _grant_tables(conn, "oos_api", app_read, select=True)
    _grant_tables(conn, "oos_worker", app_read, select=True)
    _grant_tables(conn, "oos_retention", app_read, select=True)
    _grant_tables(conn, "oos_analytics_ro", ALL_M0_TABLES, select=True)

    _grant_tables(conn, "oos_api", app_mutable, insert=True, update=True, delete=True)
    _grant_tables(conn, "oos_worker", app_mutable, insert=True, update=True, delete=True)
    _grant_tables(conn, "oos_retention", app_mutable, delete=True)

    _grant_tables(conn, "oos_api", VERSION_TABLES, insert=True, select=True)
    _grant_tables(conn, "oos_worker", VERSION_TABLES, insert=True, select=True)

    _grant_tables(conn, "oos_api", (("app", "audit_log"),), insert=True, select=True)
    _grant_tables(conn, "oos_worker", (("app", "audit_log"),), insert=True, select=True)

    for role in ("oos_api", "oos_worker"):
        audit_seq = "GRANT USAGE, SELECT ON SEQUENCE app.audit_log_id_seq TO "
        outbox_seq = "GRANT USAGE, SELECT ON SEQUENCE app.outbox_event_seq_seq TO "
        conn.execute(text(f"{audit_seq}{_pg_ident(role)}"))
        conn.execute(text(f"{outbox_seq}{_pg_ident(role)}"))

    _grant_tables(
        conn, "oos_render", M0_MEDIA_TABLES, select=True, insert=True, update=True, delete=True
    )
    _grant_tables(conn, "oos_render", M0_APP_TABLES, select=True)

    conn.execute(text("GRANT CREATE ON SCHEMA dbos TO oos_worker"))
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
        conn.execute(text(f"DROP TABLE IF EXISTS {_qualified(schema, table)} CASCADE"))
    for schema in reversed(("analytics", "media", "app", "dbos")):
        conn.execute(text(f"DROP SCHEMA IF EXISTS {_pg_ident(schema)} CASCADE"))
