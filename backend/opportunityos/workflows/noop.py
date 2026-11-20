"""Test-only no-op workflow (SPEC-09a; APP_ENV=test)."""

from __future__ import annotations

import os

from dbos import DBOS

from opportunityos.workflows.execution_steps import mark_run_started


def register_test_workflows() -> None:
    if os.environ.get("APP_ENV") != "test":
        return

    @DBOS.workflow(name="test_noop")
    def test_noop_workflow(
        request_id: str,
        workspace_id: str,
        project_id: str,
        workflow_type: str,
    ) -> None:
        mark_run_started(request_id, workspace_id, project_id, workflow_type)

    from opportunityos.workflows import dispatcher

    dispatcher.set_test_noop_workflow(test_noop_workflow)
