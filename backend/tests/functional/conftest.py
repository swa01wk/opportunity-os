"""Testcontainers PostgreSQL 17 for SPEC-04 functional tests."""

from __future__ import annotations

from collections.abc import Generator

import pytest
from m0_access import ALL_M0_TABLES
from support import alembic_upgrade, role_urls
from testcontainers.postgres import PostgresContainer


@pytest.fixture(scope="session")
def postgres_spec04() -> Generator[PostgresContainer]:
    with PostgresContainer("postgres:17") as postgres:
        yield postgres


@pytest.fixture(scope="session")
def migrated_database(postgres_spec04: PostgresContainer) -> dict[str, str]:
    urls = role_urls(postgres_spec04)
    alembic_upgrade(urls["migrate_url"])
    return urls


@pytest.fixture
def m0_table_names() -> list[str]:
    return [f"{schema}.{table}" for schema, table in ALL_M0_TABLES]
