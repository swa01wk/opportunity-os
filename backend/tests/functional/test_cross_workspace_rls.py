"""T-07 (C07 part): workspace isolation per service role and M0 table (SPEC-04 AC2)."""

from __future__ import annotations

import uuid

import pytest
from m0_access import LOGIN_ROLES, privileges_for
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from support import count_rows

pytestmark = pytest.mark.functional

WS_A = uuid.UUID("00000000-0000-4000-8000-00000000a001")
WS_B = uuid.UUID("00000000-0000-4000-8000-00000000b002")
MEMBER_A = uuid.UUID("00000000-0000-4000-8000-00000000a011")
MEMBER_B = uuid.UUID("00000000-0000-4000-8000-00000000b022")
BRAND_A = uuid.UUID("00000000-0000-4000-8000-00000000a033")
BRAND_B = uuid.UUID("00000000-0000-4000-8000-00000000b044")
PROJECT_A = uuid.UUID("00000000-0000-4000-8000-00000000a055")
PROJECT_B = uuid.UUID("00000000-0000-4000-8000-00000000b066")
RUN_A = uuid.UUID("00000000-0000-4000-8000-00000000a077")
RUN_B = uuid.UUID("00000000-0000-4000-8000-00000000b088")


def _seed_two_workspaces(migrate_url: str) -> None:
    engine = create_engine(migrate_url)
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                INSERT INTO app.workspace (id, name) VALUES
                  (:wa, 'Workspace A'),
                  (:wb, 'Workspace B')
                """
            ),
            {"wa": WS_A, "wb": WS_B},
        )
        conn.execute(
            text(
                """
                INSERT INTO app.member (
                    id, workspace_id, idp_issuer, idp_subject, display_name, responsibilities
                ) VALUES
                  (:ma, :wa, 'test', 'member-a', 'Member A', '{owner}'),
                  (:mb, :wb, 'test', 'member-b', 'Member B', '{owner}')
                """
            ),
            {"ma": MEMBER_A, "mb": MEMBER_B, "wa": WS_A, "wb": WS_B},
        )
        conn.execute(
            text(
                """
                INSERT INTO app.brand_kit (id, workspace_id, name, head_version)
                VALUES (:ba, :wa, 'Brand A', 1), (:bb, :wb, 'Brand B', 1)
                """
            ),
            {"ba": BRAND_A, "bb": BRAND_B, "wa": WS_A, "wb": WS_B},
        )
        conn.execute(
            text(
                """
                INSERT INTO app.brand_kit_version (
                    brand_kit_id, version, workspace_id, tokens, sha256, created_by
                ) VALUES
                  (:ba, 1, :wa, '{}'::jsonb,
                   'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa', :ma),
                  (:bb, 1, :wb, '{}'::jsonb,
                   'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb', :mb)
                """
            ),
            {
                "ba": BRAND_A,
                "bb": BRAND_B,
                "wa": WS_A,
                "wb": WS_B,
                "ma": MEMBER_A,
                "mb": MEMBER_B,
            },
        )
        conn.execute(
            text(
                """
                INSERT INTO app.project (
                    id, workspace_id, title, series, brand_kit_id,
                    brand_kit_version, narrator
                ) VALUES
                  (:pa, :wa, 'Project A', 'solve_this', :ba, 1, '{}'::jsonb),
                  (:pb, :wb, 'Project B', 'solve_this', :bb, 1, '{}'::jsonb)
                """
            ),
            {
                "pa": PROJECT_A,
                "pb": PROJECT_B,
                "wa": WS_A,
                "wb": WS_B,
                "ba": BRAND_A,
                "bb": BRAND_B,
            },
        )
        conn.execute(
            text(
                """
                INSERT INTO app.workflow_request (id, workspace_id, project_id, body)
                VALUES
                  (:ra, :wa, :pa, '{}'::jsonb),
                  (:rb, :wb, :pb, '{}'::jsonb)
                """
            ),
            {
                "ra": RUN_A,
                "rb": RUN_B,
                "wa": WS_A,
                "wb": WS_B,
                "pa": PROJECT_A,
                "pb": PROJECT_B,
            },
        )
        conn.execute(
            text(
                """
                INSERT INTO app.execution_run (
                    id, workspace_id, project_id, workflow_type, state
                ) VALUES
                  (:ra, :wa, :pa, 'diagnostic', 'succeeded'),
                  (:rb, :wb, :pb, 'diagnostic', 'succeeded')
                """
            ),
            {
                "ra": RUN_A,
                "rb": RUN_B,
                "wa": WS_A,
                "wb": WS_B,
                "pa": PROJECT_A,
                "pb": PROJECT_B,
            },
        )
        conn.execute(
            text(
                """
                INSERT INTO app.task_attempt (
                    id, workspace_id, run_id, task_key, task_type, attempt, status, started_at
                ) VALUES
                  (gen_random_uuid(), :wa, :ra, 't1', 'diagnostic_echo', 1, 'succeeded', now()),
                  (gen_random_uuid(), :wb, :rb, 't1', 'diagnostic_echo', 1, 'succeeded', now())
                """
            ),
            {"ra": RUN_A, "rb": RUN_B, "wa": WS_A, "wb": WS_B},
        )
        conn.execute(
            text(
                """
                INSERT INTO app.outbox_event (id, workspace_id, type, body)
                VALUES
                  (gen_random_uuid(), :wa, 'test.a', '{}'::jsonb),
                  (gen_random_uuid(), :wb, 'test.b', '{}'::jsonb)
                """
            ),
            {"wa": WS_A, "wb": WS_B},
        )
        conn.execute(
            text(
                """
                INSERT INTO app.audit_log (workspace_id, actor, action, subject)
                VALUES
                  (:wa, '{}'::jsonb, 'test', '{}'::jsonb),
                  (:wb, '{}'::jsonb, 'test', '{}'::jsonb)
                """
            ),
            {"wa": WS_A, "wb": WS_B},
        )
        conn.execute(
            text(
                """
                INSERT INTO app.idempotency_key (key, workspace_id, request_sha256, response)
                VALUES
                  ('key-a', :wa, repeat('a', 64), '{}'::jsonb),
                  ('key-b', :wb, repeat('b', 64), '{}'::jsonb)
                """
            ),
            {"wa": WS_A, "wb": WS_B},
        )
        conn.execute(
            text(
                """
                INSERT INTO media.render_job (
                    job_id, workspace_id, request, state, status
                ) VALUES
                  (repeat('a', 64), :wa, '{}'::jsonb, 'queued', '{}'::jsonb),
                  (repeat('b', 64), :wb, '{}'::jsonb, 'queued', '{}'::jsonb)
                """
            ),
            {"wa": WS_A, "wb": WS_B},
        )


@pytest.fixture(scope="module")
def two_workspaces(migrated_database: dict[str, str]) -> dict[str, str]:
    _seed_two_workspaces(migrated_database["migrate_url"])
    return migrated_database


@pytest.mark.t("T-07")
@pytest.mark.parametrize("role", LOGIN_ROLES)
def test_cross_workspace_reads_isolated(
    two_workspaces: dict[str, str],
    m0_table_names: list[str],
    role_engines: dict[str, Engine],
    role: str,
) -> None:
    engine = role_engines[role]
    for table in m0_table_names:
        schema, _, name = table.partition(".")
        privs = privileges_for(role, schema, name)
        if "SELECT" not in privs:
            with pytest.raises(Exception, match="permission denied"):
                count_rows(engine, role, str(WS_A), table)
            continue

        if table == "app.service_identity":
            total = count_rows(engine, role, str(WS_A), table)
            assert total == 0
            continue

        visible_a = count_rows(engine, role, str(WS_A), table)
        visible_b = count_rows(engine, role, str(WS_B), table)
        assert visible_a == 1, f"{role} on {table} with workspace A"
        assert visible_b == 1, f"{role} on {table} with workspace B"
        assert count_rows(engine, role, None, table) == 0, f"{role} on {table} without workspace"
