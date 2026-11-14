"""T-34: migrations, grants, seed, outbox sequence (SPEC-04 AC1, AC3-AC5)."""

from __future__ import annotations

import concurrent.futures
import os
import subprocess
import sys
import uuid

import pytest
from sqlalchemy import create_engine, text
from support import (
    TEST_PASSWORDS,
    alembic_downgrade,
    alembic_upgrade,
    normalize_schema_dump,
    pg_dump_schema_only,
    seed_row_snapshot,
)
from testcontainers.community.postgres import PostgresContainer

pytestmark = pytest.mark.functional


@pytest.mark.t("T-34")
def test_upgrade_downgrade_reupgrade_schema_unchanged(postgres_ac1: PostgresContainer) -> None:
    host = postgres_ac1.get_container_host_ip()
    port = int(postgres_ac1.get_exposed_port(5432))
    user = postgres_ac1.username
    password = postgres_ac1.password
    db = postgres_ac1.dbname
    url = f"postgresql+psycopg://{user}:{password}@{host}:{port}/{db}"

    alembic_upgrade(url)
    first_dump = normalize_schema_dump(pg_dump_schema_only(postgres_ac1))

    alembic_downgrade(url)
    alembic_upgrade(url)
    second_dump = normalize_schema_dump(pg_dump_schema_only(postgres_ac1))

    assert first_dump == second_dump


@pytest.mark.t("T-34")
def test_render_cannot_write_app_role_refused(migrated_database: dict[str, str]) -> None:
    engine = create_engine(migrated_database["oos_render"])
    with engine.connect() as conn, conn.begin():
        conn.execute(text("SET LOCAL ROLE oos_render"))
        with pytest.raises(Exception, match="permission denied"):
            conn.execute(
                text(
                    """
                    INSERT INTO app.workspace (id, name)
                    VALUES (gen_random_uuid(), 'blocked')
                    """
                ),
            )


@pytest.mark.t("T-34")
@pytest.mark.parametrize("role", ["oos_api", "oos_worker"])
def test_version_and_audit_rows_are_insert_only(
    migrated_database: dict[str, str],
    role: str,
) -> None:
    engine = create_engine(migrated_database[role])
    with engine.begin() as conn:
        conn.execute(text(f"SET LOCAL ROLE {role}"))
        with pytest.raises(Exception, match="permission denied"):
            conn.execute(text("UPDATE app.brand_kit_version SET sha256 = sha256 WHERE false"))
    with engine.begin() as conn:
        conn.execute(text(f"SET LOCAL ROLE {role}"))
        with pytest.raises(Exception, match="permission denied"):
            conn.execute(text("DELETE FROM app.audit_log"))


@pytest.mark.t("T-34")
def test_seed_idempotent_and_refuses_production(migrated_database: dict[str, str]) -> None:
    env = {
        **os.environ,
        **TEST_PASSWORDS,
        "MIGRATE_DATABASE_URL": migrated_database["migrate_url"],
        "APP_ENV": "development",
        "PYTHONPATH": str(__import__("pathlib").Path(__file__).resolve().parents[3]),
    }
    subprocess.run(
        [sys.executable, "-m", "infra.seed.load"],
        check=True,
        env=env,
        capture_output=True,
        text=True,
    )
    first_snapshot = seed_row_snapshot(migrated_database["migrate_url"])
    subprocess.run(
        [sys.executable, "-m", "infra.seed.load"],
        check=True,
        env=env,
        capture_output=True,
        text=True,
    )
    second_snapshot = seed_row_snapshot(migrated_database["migrate_url"])
    assert first_snapshot == second_snapshot

    prod_env = {**env, "APP_ENV": "production"}
    failed = subprocess.run(
        [sys.executable, "-m", "infra.seed.load"],
        env=prod_env,
        capture_output=True,
        text=True,
    )
    assert failed.returncode != 0
    assert "APP_ENV=production" in failed.stderr


@pytest.mark.t("T-34")
def test_outbox_seq_unique_under_concurrent_inserts(migrated_database: dict[str, str]) -> None:
    worker_url = migrated_database["oos_worker"]
    workspace_id = str(uuid.uuid4())

    def insert_batch(n: int) -> list[int]:
        engine = create_engine(worker_url)
        seqs: list[int] = []
        with engine.connect() as conn, conn.begin():
            conn.execute(text("SET LOCAL ROLE oos_worker"))
            conn.execute(
                text("SELECT set_config('app.workspace_id', :wid, true)"),
                {"wid": workspace_id},
            )
            for _ in range(n):
                row = conn.execute(
                    text(
                        """
                        INSERT INTO app.outbox_event (id, workspace_id, type, body)
                        VALUES (gen_random_uuid(), :ws, 'test.event', '{}'::jsonb)
                        RETURNING seq
                        """
                    ),
                    {"ws": workspace_id},
                ).one()
                seqs.append(int(row.seq))
        return seqs

    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        batches = list(pool.map(insert_batch, [5] * 8))
    all_seqs = [value for batch in batches for value in batch]
    assert len(all_seqs) == len(set(all_seqs))
    ordered = sorted(all_seqs)
    assert ordered == list(range(ordered[0], ordered[0] + len(ordered)))
