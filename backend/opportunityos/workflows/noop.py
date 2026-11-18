"""Test-only no-op workflow (SPEC-09a; APP_ENV=test)."""

from __future__ import annotations

import os
from uuid import UUID

from dbos import DBOS
from sqlalchemy import create_engine, text

from opportunityos.repo.session import workspace_transaction


def register_test_workflows() -> None:
    if os.environ.get("APP_ENV") != "test":
        return

    @DBOS.step()
    def persist_execution_run(
        request_id: str,
        workspace_id: str,
        project_id: str,
        workflow_type: str,
    ) -> None:
        engine = create_engine(os.environ["DATABASE_URL"])
        with workspace_transaction(
            engine,
            role="oos_worker",
            workspace_id=UUID(workspace_id),
        ) as conn:
            conn.execute(
                text(
                    """
                    INSERT INTO app.execution_run (
                        id, workspace_id, project_id, workflow_type, state
                    )
                    VALUES (:id, :ws, :project, :wf_type, 'running')
                    ON CONFLICT (id) DO UPDATE
                    SET state = EXCLUDED.state, workflow_type = EXCLUDED.workflow_type
                    """
                ),
                {
                    "id": request_id,
                    "ws": workspace_id,
                    "project": project_id,
                    "wf_type": workflow_type,
                },
            )

    @DBOS.workflow(name="test_noop")
    def test_noop_workflow(
        request_id: str,
        workspace_id: str,
        project_id: str,
        workflow_type: str,
    ) -> None:
        persist_execution_run(request_id, workspace_id, project_id, workflow_type)

    from opportunityos.workflows import dispatcher

    dispatcher.set_test_noop_workflow(test_noop_workflow)
