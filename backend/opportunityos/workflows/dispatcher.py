"""Claim workflow_request rows and start DBOS workflows (SPEC-09a, NFR-01)."""

from __future__ import annotations

import json
import time
from collections.abc import Callable
from typing import Any
from uuid import UUID

import structlog
from dbos import DBOS, SetWorkflowID
from opentelemetry import trace
from pydantic import ValidationError
from sqlalchemy import text
from sqlalchemy.engine import Connection, Engine

from opportunityos.workflows.claim import claim_workflow_requests
from opportunityos.workflows.metrics import DISPATCH_SECONDS
from opportunityos_contracts.events.workflow_request import WorkflowRequest, WorkflowType

_log = structlog.get_logger(__name__)
_TRACER = trace.get_tracer(__name__)

TestNoopWorkflow = Callable[[str, str, str, str], None]

_test_noop_workflow: TestNoopWorkflow | None = None
_mark_dispatched_hook: Callable[[], None] | None = None


def set_test_noop_workflow(func: TestNoopWorkflow) -> None:
    global _test_noop_workflow
    _test_noop_workflow = func


def set_mark_dispatched_hook(hook: Callable[[], None] | None) -> None:
    global _mark_dispatched_hook
    _mark_dispatched_hook = hook


def _resolve_starter(workflow_type: WorkflowType) -> TestNoopWorkflow | None:
    if workflow_type == WorkflowType.DIAGNOSTIC and _test_noop_workflow is not None:
        return _test_noop_workflow
    return None


def _load_request(conn: Connection, request_id: UUID) -> WorkflowRequest:
    row = (
        conn.execute(
            text("SELECT body FROM app.workflow_request WHERE id = :id"),
            {"id": str(request_id)},
        )
        .mappings()
        .one()
    )
    body: Any = row["body"]
    if isinstance(body, str):
        body = json.loads(body)
    return WorkflowRequest.model_validate(body)


def _insert_pending_run(
    conn: Connection,
    *,
    run_id: UUID,
    workspace_id: UUID,
    project_id: str,
    workflow_type: str,
) -> None:
    conn.execute(
        text(
            """
            INSERT INTO app.execution_run (
                id, workspace_id, project_id, workflow_type, state
            )
            VALUES (:id, :ws, :project, :wf_type, 'pending')
            ON CONFLICT (id) DO NOTHING
            """
        ),
        {
            "id": str(run_id),
            "ws": str(workspace_id),
            "project": project_id,
            "wf_type": workflow_type,
        },
    )


def _mark_dispatched(conn: Connection, *, request_id: UUID) -> None:
    if _mark_dispatched_hook is not None:
        _mark_dispatched_hook()
    conn.execute(
        text(
            """
            UPDATE app.workflow_request
            SET dispatched_at = now()
            WHERE id = :id AND dispatched_at IS NULL
            """
        ),
        {"id": str(request_id)},
    )


def dispatch_batch(engine: Engine, *, limit: int = 16) -> int:
    """Process up to ``limit`` undelivered workflow requests. Returns new starts."""
    started = 0
    with engine.connect() as conn, conn.begin():
        conn.execute(text("SET LOCAL ROLE oos_worker"))
        conn.execute(text("SELECT set_config('app.claim_bypass', '1', true)"))
        claimed = claim_workflow_requests(conn, limit=limit)
        for row in claimed:
            nested = conn.begin_nested()
            try:
                with _TRACER.start_as_current_span("workflow.start"):
                    conn.execute(
                        text("SELECT set_config('app.workspace_id', :wid, true)"),
                        {"wid": str(row.workspace_id)},
                    )
                    try:
                        request = _load_request(conn, row.row_id)
                    except ValidationError:
                        _log.error(
                            "workflow.dispatch_failed",
                            workflow_id=str(row.row_id),
                            reason="invalid_request_body",
                        )
                        nested.rollback()
                        conn.execute(
                            text(
                                """
                                UPDATE app.workflow_request
                                SET dispatched_at = now()
                                WHERE id = :id AND dispatched_at IS NULL
                                """
                            ),
                            {"id": str(row.row_id)},
                        )
                        continue
                    starter = _resolve_starter(request.workflow_type)
                    if starter is None:
                        _log.error(
                            "workflow.dispatch_failed",
                            workflow_id=str(row.row_id),
                            reason="unknown_workflow_type",
                            workflow_type=request.workflow_type.value,
                        )
                        nested.rollback()
                        continue

                    _insert_pending_run(
                        conn,
                        run_id=row.row_id,
                        workspace_id=row.workspace_id,
                        project_id=request.project_id,
                        workflow_type=request.workflow_type.value,
                    )

                    existing = DBOS.get_workflow_status(str(row.row_id))
                    t0 = time.monotonic()
                    if existing is not None:
                        _log.info(
                            "workflow.duplicate_start_ignored",
                            workflow_id=str(row.row_id),
                            workspace_id=str(row.workspace_id),
                        )
                    else:
                        with SetWorkflowID(
                            str(row.row_id),
                            workflow_id_reuse_policy="return-existing",
                        ):
                            DBOS.start_workflow(
                                starter,
                                str(row.row_id),
                                str(row.workspace_id),
                                request.project_id,
                                request.workflow_type.value,
                            )
                        started += 1
                    DISPATCH_SECONDS.record(time.monotonic() - t0)
                nested.commit()
            except Exception:
                nested.rollback()
                _log.exception(
                    "workflow.dispatch_failed",
                    workflow_id=str(row.row_id),
                    reason="start_failed",
                )
                continue
            try:
                _mark_dispatched(conn, request_id=row.row_id)
            except Exception:
                raise
    return started


def dispatch_once(engine: Engine, *, limit: int = 16) -> int:
    return dispatch_batch(engine, limit=limit)
