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
    DBOS(
        config=DBOSConfig(
            name=name,
            system_database_url=_normalize_db_url(database_url),
            dbos_system_schema="dbos",
            run_migrations=False,
            auto_upgrade=False,
            use_listen_notify=False,
        ),
    )


def launch_dbos() -> None:
    init_dbos()
    DBOS.launch()
