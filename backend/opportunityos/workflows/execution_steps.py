"""DBOS steps that write execution_run projections (SPEC-09a, R-50)."""

from __future__ import annotations

from uuid import UUID

from dbos import DBOS
from sqlalchemy import text

from opportunityos.repo.session import workspace_transaction
from opportunityos.workflows.worker_db import worker_engine


@DBOS.step()
def mark_run_started(
    request_id: str,
    workspace_id: str,
    project_id: str,
    workflow_type: str,
) -> None:
    with workspace_transaction(
        worker_engine(),
        role="oos_worker",
        workspace_id=UUID(workspace_id),
    ) as conn:
        conn.execute(
            text(
                """
                UPDATE app.execution_run
                SET state = 'running'
                WHERE id = :id
                  AND workspace_id = :ws
                  AND state = 'pending'
                """
            ),
            {"id": request_id, "ws": workspace_id},
        )
