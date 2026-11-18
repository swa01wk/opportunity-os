"""SPEC-09a write path, dispatch and relay (T-01 C01, AC1-AC5)."""

from __future__ import annotations

import concurrent.futures
import os
import uuid
from uuid import UUID

import pytest
from dbos import DBOS
from sqlalchemy import create_engine, text

from opportunityos.domain.commands import (
    AuditRecord,
    CommandReceipt,
    WriteCommand,
    build_test_workflow_event,
    execute_write_command,
    request_body_sha256,
)
from opportunityos.domain.errors import IdempotencyKeyReused
from opportunityos.repo.session import workspace_transaction
from opportunityos.workflows import dispatcher, relay
from opportunityos.workflows.dbos_runtime import init_dbos, launch_dbos
from opportunityos_contracts.common import Actor, ActorType, Responsibility

pytestmark = pytest.mark.functional

WS = UUID("00000000-0000-4000-8000-000000000201")
MEMBER = UUID("00000000-0000-4000-8000-000000000211")
BRAND = UUID("00000000-0000-4000-8000-000000000222")
PROJECT = UUID("00000000-0000-4000-8000-000000000233")


def _seed_project(migrate_url: str) -> None:
    engine = create_engine(migrate_url)
    with engine.begin() as conn:
        conn.execute(text("SET LOCAL ROLE oos_migrator"))
        conn.execute(
            text(
                """
                INSERT INTO app.workspace (id, name) VALUES (:id, 'Write path test')
                ON CONFLICT (id) DO NOTHING
                """
            ),
            {"id": str(WS)},
        )
        conn.execute(
            text(
                """
                INSERT INTO app.member (
                    id, workspace_id, idp_issuer, idp_subject, display_name, responsibilities
                ) VALUES (
                    :id, :ws, 'test', 'writer', 'Writer', '{owner}'
                )
                ON CONFLICT (id) DO NOTHING
                """
            ),
            {"id": str(MEMBER), "ws": str(WS)},
        )
        conn.execute(
            text(
                """
                INSERT INTO app.brand_kit (id, workspace_id, name, head_version)
                VALUES (:id, :ws, 'Test kit', 1)
                ON CONFLICT (id) DO NOTHING
                """
            ),
            {"id": str(BRAND), "ws": str(WS)},
        )
        conn.execute(
            text(
                """
                INSERT INTO app.brand_kit_version (
                    brand_kit_id, version, workspace_id, tokens, sha256, created_by
                ) VALUES (
                    :bk, 1, :ws, '{}'::jsonb,
                    'cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc',
                    :member
                )
                ON CONFLICT (brand_kit_id, version) DO NOTHING
                """
            ),
            {"bk": str(BRAND), "ws": str(WS), "member": str(MEMBER)},
        )
        conn.execute(
            text(
                """
                INSERT INTO app.project (
                    id, workspace_id, title, series, brand_kit_id,
                    brand_kit_version, narrator
                ) VALUES (
                    :id, :ws, 'Odd squares', 'solve_this', :bk, 1, '{}'::jsonb
                )
                ON CONFLICT (id) DO NOTHING
                """
            ),
            {"id": str(PROJECT), "ws": str(WS), "bk": str(BRAND)},
        )


def _actor() -> Actor:
    return Actor(type=ActorType.MEMBER, id=str(MEMBER), responsibility=Responsibility.OWNER)


def _run_command(
    worker_url: str,
    *,
    idempotency_key: str,
    request_body: dict[str, str],
    request_id: UUID,
    domain_fail: bool = False,
) -> tuple[CommandReceipt, bool]:
    request_hash = request_body_sha256(request_body)
    event, workflow = build_test_workflow_event(
        workspace_id=WS,
        project_id=PROJECT,
        actor=_actor(),
        request_id=request_id,
    )

    def apply(conn) -> None:
        if domain_fail:
            msg = "injected domain failure"
            raise RuntimeError(msg)
        conn.execute(
            text(
                """
                UPDATE app.project
                SET row_version = row_version + 1
                WHERE id = :id AND workspace_id = :ws
                """
            ),
            {"id": str(PROJECT), "ws": str(WS)},
        )

    command = WriteCommand(
        workspace_id=WS,
        actor=_actor(),
        idempotency_key=idempotency_key,
        request_hash=request_hash,
        audit=AuditRecord(action="test.write", subject={"type": "project", "id": str(PROJECT)}),
        outbox=event,
        workflow=workflow,
        apply_domain_change=apply,
    )
    engine = create_engine(worker_url)
    with workspace_transaction(engine, role="oos_worker", workspace_id=WS) as conn:
        return execute_write_command(conn, command)


@pytest.fixture(scope="module")
def write_path_env(migrated_database: dict[str, str]) -> dict[str, str]:
    _seed_project(migrated_database["migrate_url"])
    return migrated_database


@pytest.fixture(scope="module")
def dbos_runtime(write_path_env: dict[str, str]) -> dict[str, str]:
    os.environ["APP_ENV"] = "test"
    os.environ["DATABASE_URL"] = write_path_env["oos_worker"]
    init_dbos(name="worker-test")
    from opportunityos.workflows import noop

    noop.register_test_workflows()
    launch_dbos()
    yield write_path_env
    DBOS.destroy(destroy_registry=True)


@pytest.mark.t("T-01")
def test_duplicate_idempotency_key_same_receipt(write_path_env: dict[str, str]) -> None:
    worker_url = write_path_env["oos_worker"]
    key = f"idem-{uuid.uuid4()}"
    body = {"command": "start-diagnostic"}
    request_id = uuid.uuid4()

    def once() -> CommandReceipt:
        receipt, _ = _run_command(
            worker_url,
            idempotency_key=key,
            request_body=body,
            request_id=request_id,
        )
        return receipt

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        first, second = list(pool.map(lambda _: once(), range(2)))

    assert first.body == second.body
    engine = create_engine(worker_url)
    with workspace_transaction(engine, role="oos_worker", workspace_id=WS) as conn:
        assert (
            conn.execute(
                text("SELECT count(*)::int FROM app.workflow_request WHERE id = :id"),
                {"id": str(request_id)},
            ).scalar_one()
            == 1
        )
        assert (
            conn.execute(
                text("SELECT count(*)::int FROM app.idempotency_key WHERE key = :k"),
                {"k": key},
            ).scalar_one()
            == 1
        )


@pytest.mark.t("T-01")
def test_idempotency_key_reused_different_body(write_path_env: dict[str, str]) -> None:
    worker_url = write_path_env["oos_worker"]
    key = f"idem-{uuid.uuid4()}"
    request_id = uuid.uuid4()
    _run_command(worker_url, idempotency_key=key, request_body={"a": "1"}, request_id=request_id)
    with pytest.raises(IdempotencyKeyReused):
        _run_command(
            worker_url,
            idempotency_key=key,
            request_body={"a": "2"},
            request_id=uuid.uuid4(),
        )
    engine = create_engine(worker_url)
    with workspace_transaction(engine, role="oos_worker", workspace_id=WS) as conn:
        assert (
            conn.execute(
                text("SELECT count(*)::int FROM app.workflow_request WHERE id = :id"),
                {"id": str(request_id)},
            ).scalar_one()
            == 1
        )


def test_command_transaction_rolls_back_on_domain_failure(write_path_env: dict[str, str]) -> None:
    worker_url = write_path_env["oos_worker"]
    key = f"fail-{uuid.uuid4()}"
    request_id = uuid.uuid4()
    with pytest.raises(RuntimeError, match="injected domain failure"):
        _run_command(
            worker_url,
            idempotency_key=key,
            request_body={"fail": "true"},
            request_id=request_id,
            domain_fail=True,
        )
    engine = create_engine(worker_url)
    with workspace_transaction(engine, role="oos_worker", workspace_id=WS) as conn:
        assert (
            conn.execute(
                text("SELECT count(*)::int FROM app.workflow_request WHERE id = :id"),
                {"id": str(request_id)},
            ).scalar_one()
            == 0
        )
        assert (
            conn.execute(
                text("SELECT count(*)::int FROM app.idempotency_key WHERE key = :k"),
                {"k": key},
            ).scalar_one()
            == 0
        )


def test_lost_ack_duplicate_dispatch_is_noop(
    dbos_runtime: dict[str, str],
    write_path_env: dict[str, str],
) -> None:
    _ = dbos_runtime
    worker_url = write_path_env["oos_worker"]
    key = f"dispatch-{uuid.uuid4()}"
    request_id = uuid.uuid4()
    _run_command(worker_url, idempotency_key=key, request_body={"go": "1"}, request_id=request_id)

    duplicate_events: list[str] = []

    def fail_mark() -> None:
        msg = "lost acknowledgement"
        raise RuntimeError(msg)

    original_info = dispatcher._log.info

    def capturing_info(event: str, **kwargs: object) -> None:
        duplicate_events.append(event)
        original_info(event, **kwargs)

    dispatcher._log.info = capturing_info  # type: ignore[method-assign]
    dispatcher.set_mark_dispatched_hook(fail_mark)
    try:
        with pytest.raises(RuntimeError, match="lost acknowledgement"):
            dispatcher.dispatch_once(worker_url)
        dispatcher.set_mark_dispatched_hook(None)
        dispatcher.dispatch_once(worker_url)
    finally:
        dispatcher.set_mark_dispatched_hook(None)
        dispatcher._log.info = original_info  # type: ignore[method-assign]

    assert "workflow.duplicate_start_ignored" in duplicate_events


def test_dispatch_writes_execution_run(
    dbos_runtime: dict[str, str],
    write_path_env: dict[str, str],
) -> None:
    _ = dbos_runtime
    worker_url = write_path_env["oos_worker"]
    request_id = uuid.uuid4()
    _run_command(
        write_path_env["oos_worker"],
        idempotency_key=f"run-{uuid.uuid4()}",
        request_body={"run": "1"},
        request_id=request_id,
    )
    dispatcher.dispatch_once(worker_url)
    engine = create_engine(worker_url)
    with workspace_transaction(engine, role="oos_worker", workspace_id=WS) as conn:
        row = (
            conn.execute(
                text(
                    """
                    SELECT workflow_type, state
                    FROM app.execution_run
                    WHERE id = :id
                    """
                ),
                {"id": str(request_id)},
            )
            .mappings()
            .one()
        )
    assert row["workflow_type"] == "diagnostic"
    assert row["state"] == "running"


def test_outbox_relay_delivers_event(write_path_env: dict[str, str]) -> None:
    worker_url = write_path_env["oos_worker"]
    _run_command(
        worker_url,
        idempotency_key=f"relay-{uuid.uuid4()}",
        request_body={"relay": "1"},
        request_id=uuid.uuid4(),
    )
    delivered: list[str] = []

    def sink(payload: dict[str, object]) -> None:
        delivered.append(str(payload["type"]))

    relay.relay_once(worker_url, sinks=(sink,))
    assert delivered == ["workflow.requested"]
