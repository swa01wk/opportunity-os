"""DBOS system schema migration outside Alembic transactions (SPEC-09a, ADR-003)."""

from __future__ import annotations

import logging
import os
from urllib.parse import quote, urlsplit, urlunsplit

from dbos import DBOS

_log = logging.getLogger("migrations.dbos_system")

_LOCK_TIMEOUT = "30s"


def _normalize_db_url(url: str) -> str:
    if url.startswith("postgresql+psycopg://"):
        return "postgresql://" + url.removeprefix("postgresql+psycopg://")
    return url


def _migrator_url(url: str) -> str:
    """Connect as ``oos_migrator`` so DBOS objects match SPEC-04 default privileges."""
    parts = urlsplit(url)
    option_value = quote(f"-c role=oos_migrator -c lock_timeout={_LOCK_TIMEOUT}", safe="")
    query = f"options={option_value}"
    if parts.query:
        query = f"{parts.query}&{query}"
    return urlunsplit((parts.scheme, parts.netloc, parts.path, query, parts.fragment))


def migrate_dbos_system(url: str) -> None:
    schema = os.environ.get("DBOS_SYSTEM_SCHEMA", "dbos")
    DBOS.migrate(
        system_database_url=_normalize_db_url(_migrator_url(url)),
        schema=schema,
        application_role="oos_worker",
    )
    _log.info('{"event":"migration.dbos_applied","schema":"%s"}', schema)


def main() -> None:
    migrate_dbos_system(os.environ["MIGRATE_DATABASE_URL"])


if __name__ == "__main__":
    main()
