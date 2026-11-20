"""SQLAlchemy implementation of the write-path port (SPEC-09a)."""

from __future__ import annotations

import json
import uuid
from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.engine import Connection

from opportunityos.domain.commands import PLACEHOLDER_RESPONSE
from opportunityos_contracts.common import Actor
from opportunityos_contracts.events.domain_event import DomainEvent
from opportunityos_contracts.events.workflow_request import WorkflowRequest


class SqlWritePathPort:
    """Write-path port backed by a single connection inside a workspace transaction."""

    __slots__ = ("_conn",)

    def __init__(self, conn: Connection) -> None:
        self._conn = conn

    @property
    def connection(self) -> Connection:
        """Same connection as the port (application/tests only; not part of the domain port)."""
        return self._conn

    def insert_idempotency_placeholder(
        self,
        *,
        workspace_id: UUID,
        key: str,
        request_hash: str,
    ) -> None:
        self._conn.execute(
            text(
                """
                INSERT INTO app.idempotency_key (key, workspace_id, request_sha256, response)
                VALUES (:key, :ws, :hash, CAST(:response AS jsonb))
                ON CONFLICT (workspace_id, key) DO NOTHING
                """
            ),
            {
                "key": key,
                "ws": str(workspace_id),
                "hash": request_hash,
                "response": json.dumps(PLACEHOLDER_RESPONSE),
            },
        )

    def lock_idempotency_row(
        self,
        *,
        workspace_id: UUID,
        key: str,
    ) -> tuple[str, dict[str, Any]] | None:
        row = (
            self._conn.execute(
                text(
                    """
                    SELECT request_sha256, response
                    FROM app.idempotency_key
                    WHERE workspace_id = :ws AND key = :key
                    FOR UPDATE
                    """
                ),
                {"ws": str(workspace_id), "key": key},
            )
            .mappings()
            .first()
        )
        if row is None:
            return None
        response = dict(row["response"])
        return str(row["request_sha256"]), response

    def write_audit(
        self,
        *,
        workspace_id: UUID,
        actor: Actor,
        action: str,
        subject: dict[str, Any],
        request_id: UUID | None,
        trace_id: str | None,
    ) -> None:
        self._conn.execute(
            text(
                """
                INSERT INTO app.audit_log (
                    workspace_id, actor, action, subject, request_id, trace_id, at
                )
                VALUES (
                    :ws,
                    CAST(:actor AS jsonb),
                    :action,
                    CAST(:subject AS jsonb),
                    :request_id,
                    :trace_id,
                    :at
                )
                """
            ),
            {
                "ws": str(workspace_id),
                "actor": actor.model_dump_json(by_alias=True),
                "action": action,
                "subject": json.dumps(subject),
                "request_id": str(request_id) if request_id else None,
                "trace_id": trace_id,
                "at": datetime.now(tz=UTC),
            },
        )

    def write_outbox(
        self,
        *,
        workspace_id: UUID,
        event: DomainEvent,
        traceparent: str | None,
    ) -> UUID:
        event_body = event.model_copy(update={"traceparent": traceparent})
        outbox_id = uuid.uuid4()
        self._conn.execute(
            text(
                """
                INSERT INTO app.outbox_event (id, workspace_id, type, body)
                VALUES (:id, :ws, :type, CAST(:body AS jsonb))
                """
            ),
            {
                "id": str(outbox_id),
                "ws": str(workspace_id),
                "type": event.type.value,
                "body": event_body.model_dump_json(by_alias=True),
            },
        )
        return outbox_id

    def write_workflow_request(
        self,
        *,
        workspace_id: UUID,
        workflow: WorkflowRequest,
    ) -> UUID:
        request_id = UUID(workflow.request_id)
        self._conn.execute(
            text(
                """
                INSERT INTO app.workflow_request (id, workspace_id, project_id, body)
                VALUES (:id, :ws, :project_id, CAST(:body AS jsonb))
                """
            ),
            {
                "id": str(request_id),
                "ws": str(workspace_id),
                "project_id": workflow.project_id,
                "body": workflow.model_dump_json(by_alias=True, exclude_none=True),
            },
        )
        return request_id

    def finalize_idempotency(
        self,
        *,
        workspace_id: UUID,
        key: str,
        receipt_body: dict[str, Any],
    ) -> None:
        self._conn.execute(
            text(
                """
                UPDATE app.idempotency_key
                SET response = CAST(:response AS jsonb)
                WHERE workspace_id = :ws AND key = :key
                """
            ),
            {
                "ws": str(workspace_id),
                "key": key,
                "response": json.dumps(receipt_body),
            },
        )
