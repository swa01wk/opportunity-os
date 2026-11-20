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


@pytest.mark.t("T-34")
@pytest.mark.parametrize("role", ["oos_api", "oos_render", "oos_retention", "oos_analytics_ro"])
def test_claim_functions_not_executable_by_non_worker_roles(
    migrated_database: dict[str, str],
    role: str,
) -> None:
    engine = create_engine(migrated_database[role])
    for stmt in (
        "SELECT app.claim_workflow_requests(1)",
        "SELECT app.claim_outbox_events(1)",
    ):
        with engine.connect() as conn, conn.begin():
            conn.execute(text(f"SET LOCAL ROLE {role}"))
            with pytest.raises(Exception, match=r"permission denied|InsufficientPrivilege"):
                conn.execute(text(stmt))


@pytest.mark.t("T-34")
def test_claim_functions_executable_by_worker(migrated_database: dict[str, str]) -> None:
    engine = create_engine(migrated_database["oos_worker"])
    with engine.connect() as conn, conn.begin():
        conn.execute(text("SET LOCAL ROLE oos_worker"))
        conn.execute(text("SELECT app.claim_workflow_requests(0)"))
        conn.execute(text("SELECT app.claim_outbox_events(0)"))


@pytest.mark.t("T-34")
@pytest.mark.parametrize("role", ["oos_worker", "oos_api", "oos_render"])
def test_cannot_set_role_oos_claim(migrated_database: dict[str, str], role: str) -> None:
    engine = create_engine(migrated_database[role])
    with engine.connect() as conn, conn.begin():
        conn.execute(text(f"SET LOCAL ROLE {role}"))
        with pytest.raises(Exception, match=r"permission denied|cannot set"):
            conn.execute(text("SET LOCAL ROLE oos_claim"))


@pytest.mark.t("T-34")
def test_claim_does_not_widen_worker_visibility_across_workspaces(
    migrated_database: dict[str, str],
) -> None:
    ws_a = uuid.UUID("00000000-0000-4000-8000-00000000a301")
    ws_b = uuid.UUID("00000000-0000-4000-8000-00000000b302")
    proj_a = uuid.UUID("00000000-0000-4000-8000-00000000a311")
    proj_b = uuid.UUID("00000000-0000-4000-8000-00000000b322")
    req_a = uuid.UUID("00000000-0000-4000-8000-00000000a333")
    req_b = uuid.UUID("00000000-0000-4000-8000-00000000b344")
    brand = uuid.UUID("00000000-0000-4000-8000-00000000c355")
    member = uuid.UUID("00000000-0000-4000-8000-00000000c366")
    migrate = create_engine(migrated_database["migrate_url"])
    with migrate.begin() as conn:
        conn.execute(
            text(
                """
                INSERT INTO app.workspace (id, name) VALUES
                  (:wa, 'Claim A'), (:wb, 'Claim B')
                ON CONFLICT (id) DO NOTHING
                """
            ),
            {"wa": ws_a, "wb": ws_b},
        )
        conn.execute(
            text(
                """
                INSERT INTO app.member (
                    id, workspace_id, idp_issuer, idp_subject, display_name, responsibilities
                ) VALUES (:m, :wa, 'test', 'claim-seed', 'Claim seed', '{owner}')
                ON CONFLICT (id) DO NOTHING
                """
            ),
            {"m": member, "wa": ws_a},
        )
        conn.execute(
            text(
                """
                INSERT INTO app.brand_kit (id, workspace_id, name, head_version)
                VALUES (:bk, :wa, 'Claim seed kit', 1)
                ON CONFLICT (id) DO NOTHING
                """
            ),
            {"bk": brand, "wa": ws_a},
        )
        conn.execute(
            text(
                """
                INSERT INTO app.brand_kit_version (
                    brand_kit_id, version, workspace_id, tokens, sha256, created_by
                ) VALUES (
                    :bk, 1, :wa, '{}'::jsonb,
                    repeat('c', 64), :m
                )
                ON CONFLICT (brand_kit_id, version) DO NOTHING
                """
            ),
            {"bk": brand, "wa": ws_a, "m": member},
        )
        conn.execute(
            text(
                """
                INSERT INTO app.project (
                    id, workspace_id, title, series, brand_kit_id, brand_kit_version, narrator
                )
                VALUES (:pa, :wa, 'Pa', 'solve_this', :bk, 1, '{}'::jsonb),
                       (:pb, :wb, 'Pb', 'solve_this', :bk, 1, '{}'::jsonb)
                ON CONFLICT (id) DO NOTHING
                """
            ),
            {"pa": proj_a, "pb": proj_b, "wa": ws_a, "wb": ws_b, "bk": brand},
        )
        conn.execute(
            text(
                """
                INSERT INTO app.workflow_request (id, workspace_id, project_id, body, created_at)
                VALUES (:ra, :wa, :pa, '{}'::jsonb, now() - interval '2 minutes'),
                       (:rb, :wb, :pb, '{}'::jsonb, now() - interval '1 minute')
                ON CONFLICT (id) DO NOTHING
                """
            ),
            {
                "ra": req_a,
                "rb": req_b,
                "wa": ws_a,
                "wb": ws_b,
                "pa": proj_a,
                "pb": proj_b,
            },
        )
        conn.execute(
            text(
                """
                INSERT INTO app.outbox_event (id, workspace_id, type, body, created_at)
                VALUES (
                    gen_random_uuid(), :wa, 'test.claim', '{}'::jsonb,
                    now() - interval '2 minutes'
                ),
                (
                    gen_random_uuid(), :wb, 'test.claim', '{}'::jsonb,
                    now() - interval '1 minute'
                )
                """
            ),
            {"wa": ws_a, "wb": ws_b},
        )
    worker = create_engine(migrated_database["oos_worker"])
    with worker.connect() as conn, conn.begin():
        conn.execute(text("SET LOCAL ROLE oos_worker"))
        conn.execute(
            text("SELECT set_config('app.workspace_id', :wid, true)"),
            {"wid": str(ws_a)},
        )
        conn.execute(text("SELECT app.claim_workflow_requests(1)"))
        wf_b = conn.execute(
            text("SELECT count(*)::int FROM app.workflow_request WHERE workspace_id = :wb"),
            {"wb": str(ws_b)},
        ).scalar_one()
        out_b = conn.execute(
            text("SELECT count(*)::int FROM app.outbox_event WHERE workspace_id = :wb"),
            {"wb": str(ws_b)},
        ).scalar_one()
    assert wf_b == 0
    assert out_b == 0


@pytest.mark.t("T-34")
def test_claim_function_result_columns(migrated_database: dict[str, str]) -> None:
    engine = create_engine(migrated_database["oos_worker"])
    with engine.connect() as conn, conn.begin():
        conn.execute(text("SET LOCAL ROLE oos_worker"))
        result = conn.execute(text("SELECT * FROM app.claim_workflow_requests(0)"))
        assert list(result.keys()) == ["id", "workspace_id"]
        result2 = conn.execute(text("SELECT * FROM app.claim_outbox_events(0)"))
        assert list(result2.keys()) == ["id", "workspace_id"]


@pytest.mark.t("T-34")
def test_claim_downgrade_drops_role_and_policies(postgres_ac1: PostgresContainer) -> None:
    host = postgres_ac1.get_container_host_ip()
    port = int(postgres_ac1.get_exposed_port(5432))
    user = postgres_ac1.username
    password = postgres_ac1.password
    db = postgres_ac1.dbname
    url = f"postgresql+psycopg://{user}:{password}@{host}:{port}/{db}"
    alembic_upgrade(url)
    alembic_downgrade(url, revision="04m0baseline0001")
    engine = create_engine(url)
    with engine.connect() as conn:
        role = conn.execute(text("SELECT 1 FROM pg_roles WHERE rolname = 'oos_claim'")).first()
        assert role is None
        pol = conn.execute(
            text(
                """
                SELECT 1 FROM pg_policies
                WHERE schemaname = 'app' AND policyname LIKE 'claim_fn_%'
                """
            )
        ).first()
        assert pol is None
