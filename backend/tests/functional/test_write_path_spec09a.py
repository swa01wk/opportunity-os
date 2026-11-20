"""SPEC-09a write path, dispatch and relay (T-01 C01, AC1-AC5)."""

from __future__ import annotations

import concurrent.futures
import json
import os
import time
import uuid
from typing import Any
from uuid import UUID

import pytest
from dbos import DBOS
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from opportunityos.domain.commands import (
    AuditRecord,
    CommandReceipt,
    WriteCommand,
    build_test_workflow_event,
    execute_write_command,
    request_body_sha256,
)
from opportunityos.domain.errors import IdempotencyKeyReused
from opportunityos.domain.write_path_port import WritePathPort
from opportunityos.repo.session import workspace_transaction
from opportunityos.repo.write_path import SqlWritePathPort
from opportunityos.workflows import dispatcher, relay
from opportunityos.workflows.dbos_runtime import init_dbos, launch_dbos
from opportunityos.workflows.poll import worker_poll_cycle
from opportunityos.workflows.worker_db import dispose_worker_engine, worker_engine
from opportunityos_contracts.common import Actor, ActorType, Responsibility

pytestmark = pytest.mark.functional

WS = UUID("00000000-0000-4000-8000-000000000201")
MEMBER = UUID("00000000-0000-4000-8000-000000000211")
BRAND = UUID("00000000-0000-4000-8000-000000000222")
PROJECT = UUID("00000000-0000-4000-8000-000000000233")


def _seed_project(migrate_url: str) -> None:
    engine = create_engine(migrate_url)
    with engine.begin() as conn:
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
    engine: Engine,
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

    def apply(port: WritePathPort) -> None:
        if domain_fail:
            msg = "injected domain failure"
            raise RuntimeError(msg)
        assert isinstance(port, SqlWritePathPort)
        port.connection.execute(
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
    with workspace_transaction(engine, role="oos_worker", workspace_id=WS) as conn:
        port = SqlWritePathPort(conn)
        return execute_write_command(port, command)


def _run_state(engine: Engine, request_id: UUID) -> str | None:
    with workspace_transaction(engine, role="oos_worker", workspace_id=WS) as conn:
        return conn.execute(
            text("SELECT state FROM app.execution_run WHERE id = :id"),
            {"id": str(request_id)},
        ).scalar_one_or_none()


def _poll_run_state(engine: Engine, request_id: UUID, *, want: str, deadline: float) -> None:
    while time.monotonic() < deadline:
        state = _run_state(engine, request_id)
        if state == want:
            return
    msg = f"execution_run {request_id} not {want!r} before deadline"
    raise AssertionError(msg)


@pytest.fixture(scope="module")
def write_path_env(migrated_database: dict[str, str]) -> dict[str, str]:
    _seed_project(migrated_database["migrate_url"])
    return migrated_database


@pytest.fixture(scope="module")
def worker_db_engine(write_path_env: dict[str, str]) -> Engine:
    os.environ["APP_ENV"] = "test"
    os.environ["DATABASE_URL"] = write_path_env["oos_worker"]
    os.environ.setdefault("DBOS_SYS_DB_POOL_SIZE", "5")
    os.environ.setdefault("DBOS_MAX_EXECUTOR_THREADS", "8")
    init_dbos(name="worker-test")
    from opportunityos.workflows import noop

    noop.register_test_workflows()
    launch_dbos()
    engine = worker_engine()
    yield engine
    DBOS.destroy(destroy_registry=True)
    dispose_worker_engine()


@pytest.mark.t("T-01")
def test_duplicate_idempotency_key_same_receipt(worker_db_engine: Engine) -> None:
    key = f"idem-{uuid.uuid4()}"
    body = {"command": "start-diagnostic"}
    request_id = uuid.uuid4()

    def once() -> CommandReceipt:
        receipt, _ = _run_command(
            worker_db_engine,
            idempotency_key=key,
            request_body=body,
            request_id=request_id,
        )
        return receipt

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        first, second = list(pool.map(lambda _: once(), range(2)))

    assert first.body == second.body
    assert first.body["requestId"] == str(request_id)
    assert first.body["eventId"]
    with workspace_transaction(worker_db_engine, role="oos_worker", workspace_id=WS) as conn:
        assert (
            conn.execute(
                text("SELECT count(*)::int FROM app.workflow_request WHERE id = :id"),
                {"id": str(request_id)},
            ).scalar_one()
            == 1
        )


@pytest.mark.t("T-01")
def test_idempotency_key_reused_different_body(worker_db_engine: Engine) -> None:
    key = f"idem-{uuid.uuid4()}"
    request_id = uuid.uuid4()
    _run_command(
        worker_db_engine,
        idempotency_key=key,
        request_body={"a": "1"},
        request_id=request_id,
    )
    with pytest.raises(IdempotencyKeyReused):
        _run_command(
            worker_db_engine,
            idempotency_key=key,
            request_body={"a": "2"},
            request_id=uuid.uuid4(),
        )


def test_command_transaction_rolls_back_on_domain_failure(worker_db_engine: Engine) -> None:
    key = f"fail-{uuid.uuid4()}"
    request_id = uuid.uuid4()
    with pytest.raises(RuntimeError, match="injected domain failure"):
        _run_command(
            worker_db_engine,
            idempotency_key=key,
            request_body={"fail": "true"},
            request_id=request_id,
            domain_fail=True,
        )
    with workspace_transaction(worker_db_engine, role="oos_worker", workspace_id=WS) as conn:
        assert (
            conn.execute(
                text("SELECT count(*)::int FROM app.workflow_request WHERE id = :id"),
                {"id": str(request_id)},
            ).scalar_one()
            == 0
        )


def test_lost_ack_duplicate_dispatch_is_noop(worker_db_engine: Engine) -> None:
    request_id = uuid.uuid4()
    _run_command(
        worker_db_engine,
        idempotency_key=f"dispatch-{uuid.uuid4()}",
        request_body={"go": "1"},
        request_id=request_id,
    )

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
            dispatcher.dispatch_once(worker_db_engine)
        dispatcher.set_mark_dispatched_hook(None)
        dispatcher.dispatch_once(worker_db_engine)
    finally:
        dispatcher.set_mark_dispatched_hook(None)
        dispatcher._log.info = original_info  # type: ignore[method-assign]

    assert "workflow.duplicate_start_ignored" in duplicate_events
    assert DBOS.get_workflow_status(str(request_id)) is not None
    deadline = time.monotonic() + 30.0
    steps: list[Any] = []
    while time.monotonic() < deadline:
        steps = DBOS.list_workflow_steps(str(request_id))
        if len(steps) == 1:
            break
    assert len(steps) == 1
    with workspace_transaction(worker_db_engine, role="oos_worker", workspace_id=WS) as conn:
        assert (
            conn.execute(
                text("SELECT count(*)::int FROM app.execution_run WHERE id = :id"),
                {"id": str(request_id)},
            ).scalar_one()
            == 1
        )


def test_dispatch_writes_execution_run_pending_then_running(worker_db_engine: Engine) -> None:
    request_id = uuid.uuid4()
    _run_command(
        worker_db_engine,
        idempotency_key=f"run-{uuid.uuid4()}",
        request_body={"run": "1"},
        request_id=request_id,
    )
    dispatcher.dispatch_once(worker_db_engine)
    assert _run_state(worker_db_engine, request_id) == "pending"
    _poll_run_state(
        worker_db_engine,
        request_id,
        want="running",
        deadline=time.monotonic() + 30.0,
    )


def test_worker_poll_cycle_dispatches_and_relays(worker_db_engine: Engine) -> None:
    request_id = uuid.uuid4()
    _run_command(
        worker_db_engine,
        idempotency_key=f"poll-{uuid.uuid4()}",
        request_body={"poll": "1"},
        request_id=request_id,
    )
    deadline = time.monotonic() + 30.0
    dispatched = False
    delivered = False
    while time.monotonic() < deadline:
        worker_poll_cycle(worker_db_engine)
        with workspace_transaction(worker_db_engine, role="oos_worker", workspace_id=WS) as conn:
            dispatched = conn.execute(
                text(
                    "SELECT dispatched_at IS NOT NULL FROM app.workflow_request WHERE id = :id",
                ),
                {"id": str(request_id)},
            ).scalar_one()
            delivered = conn.execute(
                text(
                    """
                    SELECT delivered_at IS NOT NULL
                    FROM app.outbox_event
                    WHERE type = 'workflow.requested'
                      AND body->>'correlationId' = :rid
                    ORDER BY seq DESC
                    LIMIT 1
                    """
                ),
                {"rid": str(request_id)},
            ).scalar_one_or_none()
        if dispatched and delivered is True:
            break
    assert dispatched is True
    assert delivered is True


def test_dispatch_skips_unknown_workflow_type(
    worker_db_engine: Engine,
    write_path_env: dict[str, str],
) -> None:
    blocked_id = uuid.uuid4()
    good_id = uuid.uuid4()
    blocked_body = {
        "requestId": str(blocked_id),
        "workflowType": "research",
        "projectId": str(PROJECT),
        "requestedBy": _actor().model_dump(by_alias=True),
        "input": {},
    }
    seed_engine = create_engine(write_path_env["migrate_url"])
    with seed_engine.begin() as conn:
        conn.execute(
            text(
                """
                INSERT INTO app.workflow_request (id, workspace_id, project_id, body, created_at)
                VALUES (:id, :ws, :project, CAST(:body AS jsonb), now() - interval '1 hour')
                """
            ),
            {
                "id": str(blocked_id),
                "ws": str(WS),
                "project": str(PROJECT),
                "body": json.dumps(blocked_body),
            },
        )
    _run_command(
        worker_db_engine,
        idempotency_key=f"good-{uuid.uuid4()}",
        request_body={"good": "1"},
        request_id=good_id,
    )
    dispatcher.dispatch_once(worker_db_engine, limit=8)
    with workspace_transaction(worker_db_engine, role="oos_worker", workspace_id=WS) as conn:
        blocked = conn.execute(
            text("SELECT dispatched_at FROM app.workflow_request WHERE id = :id"),
            {"id": str(blocked_id)},
        ).scalar_one()
        good = conn.execute(
            text("SELECT dispatched_at IS NOT NULL FROM app.workflow_request WHERE id = :id"),
            {"id": str(good_id)},
        ).scalar_one()
    assert blocked is None
    assert good is True


def test_relay_stops_at_sink_failure_keeps_prior_delivered(worker_db_engine: Engine) -> None:
    _run_command(
        worker_db_engine,
        idempotency_key=f"relay-a-{uuid.uuid4()}",
        request_body={"relay": "a"},
        request_id=uuid.uuid4(),
    )
    _run_command(
        worker_db_engine,
        idempotency_key=f"relay-b-{uuid.uuid4()}",
        request_body={"relay": "b"},
        request_id=uuid.uuid4(),
    )

    calls: list[int] = []

    def sink(payload: dict[str, Any]) -> None:
        if calls:
            msg = "sink failure"
            raise RuntimeError(msg)
        calls.append(int(payload["seq"]))

    delivered = relay.relay_once(worker_db_engine, sinks=(sink,))
    assert delivered == 1
    assert len(calls) == 1
