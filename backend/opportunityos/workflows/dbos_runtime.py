"""DBOS worker configuration (ADR-003, SPEC-09a)."""

from __future__ import annotations

import os

from dbos import DBOS, DBOSConfig


def _normalize_db_url(url: str) -> str:
    if url.startswith("postgresql+psycopg://"):
        return "postgresql://" + url.removeprefix("postgresql+psycopg://")
    return url


def init_dbos(*, name: str = "worker") -> None:
    database_url = os.environ["DATABASE_URL"]
    schema = os.environ.get("DBOS_SYSTEM_SCHEMA", "dbos")
    pool_size = int(os.environ.get("DBOS_SYS_DB_POOL_SIZE", "5"))
    max_threads = int(os.environ.get("DBOS_MAX_EXECUTOR_THREADS", "8"))
    DBOS(
        config=DBOSConfig(
            name=name,
            system_database_url=_normalize_db_url(database_url),
            dbos_system_schema=schema,
            sys_db_pool_size=pool_size,
            max_executor_threads=max_threads,
            run_migrations=False,
            auto_upgrade=False,
            use_listen_notify=False,
        ),
    )


def launch_dbos() -> None:
    DBOS.launch()
