"""Shared helpers for SPEC-04 functional tests."""

from __future__ import annotations

import os
import re
from pathlib import Path

from alembic import command
from alembic.config import Config
from m0_access import ENV_PASSWORD_KEYS, LOGIN_ROLES
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from testcontainers.postgres import PostgresContainer

REPO_ROOT = Path(__file__).resolve().parents[3]

TEST_PASSWORDS: dict[str, str] = {
    "DB_PASSWORD_API": "test-password-api",
    "DB_PASSWORD_WORKER": "test-password-worker",
    "DB_PASSWORD_RENDER": "test-password-render",
    "DB_PASSWORD_RETENTION": "test-password-retention",
    "DB_PASSWORD_ANALYTICS_RO": "test-password-analytics-ro",
}


def alembic_upgrade(url: str, *, revision: str = "head") -> None:
    os.environ["MIGRATE_DATABASE_URL"] = url
    for key, value in TEST_PASSWORDS.items():
        os.environ[key] = value
    cfg = Config(str(REPO_ROOT / "backend" / "alembic.ini"))
    command.upgrade(cfg, revision)


def alembic_downgrade(url: str, *, revision: str = "base") -> None:
    os.environ["MIGRATE_DATABASE_URL"] = url
    for key, value in TEST_PASSWORDS.items():
        os.environ[key] = value
    cfg = Config(str(REPO_ROOT / "backend" / "alembic.ini"))
    command.downgrade(cfg, revision)


def normalize_schema_dump(raw: str) -> str:
    lines: list[str] = []
    for line in raw.splitlines():
        if line.startswith("--") or line.startswith("\\"):
            continue
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("SET ") or stripped.startswith("SELECT pg_catalog"):
            continue
        lines.append(line)
    return "\n".join(lines)


def pg_dump_schema_only(container: PostgresContainer) -> str:
    password = container.password
    db = container.dbname
    user = container.username
    prev = os.environ.get("PGPASSWORD")
    os.environ["PGPASSWORD"] = password
    try:
        result = container.exec(
            [
                "pg_dump",
                "-U",
                user,
                "--schema-only",
                "--no-owner",
                db,
            ],
        )
    finally:
        if prev is None:
            os.environ.pop("PGPASSWORD", None)
        else:
            os.environ["PGPASSWORD"] = prev
    exit_code, output = result  # type: ignore[misc]
    if exit_code != 0:
        msg = f"pg_dump failed ({exit_code}): {output!r}"
        raise RuntimeError(msg)
    if isinstance(output, bytes):
        return output.decode("utf-8")
    return str(output)


def role_urls(container: PostgresContainer) -> dict[str, str]:
    host = container.get_container_host_ip()
    port = int(container.get_exposed_port(5432))
    db = container.dbname
    migrate_user = container.username
    migrate_password = container.password
    migrate_url = f"postgresql+psycopg://{migrate_user}:{migrate_password}@{host}:{port}/{db}"
    urls = {
        "migrate_url": migrate_url,
        "host": host,
        "port": str(port),
        "dbname": db,
    }
    for role in LOGIN_ROLES:
        password = TEST_PASSWORDS[ENV_PASSWORD_KEYS[role]]
        urls[role] = f"postgresql+psycopg://{role}:{password}@{host}:{port}/{db}"
    return urls


def engines_for_roles(urls: dict[str, str]) -> dict[str, Engine]:
    return {role: create_engine(urls[role]) for role in LOGIN_ROLES}


def count_rows(engine: Engine, role: str, workspace_id: str | None, table: str) -> int:
    schema, _, table_name = table.partition(".")
    if not re.fullmatch(r"[a-z_][a-z0-9_]*", schema) or not re.fullmatch(
        r"[a-z_][a-z0-9_]*", table_name
    ):
        msg = f"invalid table name: {table!r}"
        raise ValueError(msg)
    with engine.connect() as conn, conn.begin():
        conn.execute(text(f"SET LOCAL ROLE {role}"))
        if workspace_id is not None:
            conn.execute(
                text("SELECT set_config('app.workspace_id', :wid, true)"),
                {"wid": workspace_id},
            )
        sql = f"SELECT count(*)::int FROM {schema}.{table_name}"
        result = conn.execute(text(sql))
        return int(result.scalar_one())


def seed_row_snapshot(migrate_url: str) -> list[dict[str, object]]:
    """Canonical rows written by infra.seed.load (AC4 idempotence)."""
    engine = create_engine(migrate_url)
    with engine.begin() as conn:
        conn.execute(text("SET LOCAL ROLE oos_migrator"))
        conn.execute(
            text("SELECT set_config('app.workspace_id', :wid, true)"),
            {"wid": "00000000-0000-4000-8000-000000000001"},
        )
        project = (
            conn.execute(text("SELECT id::text, title, series, state FROM app.project ORDER BY id"))
            .mappings()
            .all()
        )
        workspace = (
            conn.execute(text("SELECT id::text, name FROM app.workspace ORDER BY id"))
            .mappings()
            .all()
        )
        members = (
            conn.execute(
                text("SELECT id::text, idp_subject, display_name FROM app.member ORDER BY id")
            )
            .mappings()
            .all()
        )
        identities = (
            conn.execute(text("SELECT id, kind FROM app.service_identity ORDER BY id"))
            .mappings()
            .all()
        )
        kits = (
            conn.execute(text("SELECT id::text, name, head_version FROM app.brand_kit ORDER BY id"))
            .mappings()
            .all()
        )
    return [
        {"workspace": [dict(r) for r in workspace]},
        {"member": [dict(r) for r in members]},
        {"service_identity": [dict(r) for r in identities]},
        {"brand_kit": [dict(r) for r in kits]},
        {"project": [dict(r) for r in project]},
    ]
