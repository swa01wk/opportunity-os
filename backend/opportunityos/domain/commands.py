"""Consequential write path: idempotency, audit, outbox and workflow request (SPEC-09a)."""

from __future__ import annotations

import hashlib
import json
import uuid
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.engine import Connection

from opportunityos.domain.errors import IdempotencyKeyReused
from opportunityos.telemetry.business_metrics import record_idempotency_replay
from opportunityos.telemetry.propagation import current_traceparent
from opportunityos_contracts.common import Actor
from opportunityos_contracts.events.domain_event import DomainEvent, DomainEventSubject, EventType
from opportunityos_contracts.events.workflow_request import (
    WorkflowRequest,
    WorkflowRequestInput,
    WorkflowType,
)

PLACEHOLDER_RESPONSE: dict[str, Any] = {"_pending": True}


def request_body_sha256(body: dict[str, Any]) -> str:
    canonical = json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


@dataclass(frozen=True, slots=True)
class AuditRecord:
    action: str
    subject: dict[str, Any]
    request_id: UUID | None = None


@dataclass(frozen=True, slots=True)
class CommandReceipt:
    """Stored as idempotency response and returned to callers (C01)."""

    body: dict[str, Any]


@dataclass(frozen=True, slots=True)
class WriteCommand:
    workspace_id: UUID
    actor: Actor
    idempotency_key: str
    request_hash: str
    audit: AuditRecord
    outbox: DomainEvent
    workflow: WorkflowRequest | None
    apply_domain_change: Callable[[Connection], None]


def _trace_id_from_traceparent(traceparent: str | None) -> str | None:
    if not traceparent:
        return None
    parts = traceparent.split("-")
    if len(parts) >= 2:
        return parts[1]
    return None


def _insert_idempotency_placeholder(
    conn: Connection,
    *,
    workspace_id: UUID,
    key: str,
    request_hash: str,
) -> None:
    conn.execute(
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


def _lock_idempotency_row(
    conn: Connection,
    *,
    workspace_id: UUID,
    key: str,
) -> tuple[str, dict[str, Any]] | None:
    row = (
        conn.execute(
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


def _write_audit(
    conn: Connection,
    *,
    workspace_id: UUID,
    actor: Actor,
    audit: AuditRecord,
    trace_id: str | None,
) -> None:
    conn.execute(
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
            "action": audit.action,
            "subject": json.dumps(audit.subject),
            "request_id": str(audit.request_id) if audit.request_id else None,
            "trace_id": trace_id,
            "at": datetime.now(tz=UTC),
        },
    )


def _write_outbox(conn: Connection, *, workspace_id: UUID, event: DomainEvent) -> uuid.UUID:
    traceparent = current_traceparent() or event.traceparent
    event_body = event.model_copy(update={"traceparent": traceparent})
    outbox_id = uuid.uuid4()
    conn.execute(
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


def _write_workflow_request(
    conn: Connection,
    *,
    workspace_id: UUID,
    workflow: WorkflowRequest,
) -> uuid.UUID:
    request_id = uuid.UUID(workflow.request_id)
    conn.execute(
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


def _finalize_idempotency(
    conn: Connection,
    *,
    workspace_id: UUID,
    key: str,
    receipt: CommandReceipt,
) -> None:
    conn.execute(
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
            "response": json.dumps(receipt.body),
        },
    )


def execute_write_command(conn: Connection, command: WriteCommand) -> tuple[CommandReceipt, bool]:
    """Run the write path in an open transaction (caller sets role and workspace).

    Returns the receipt and whether this call was a replay of a completed command.
    """
    _insert_idempotency_placeholder(
        conn,
        workspace_id=command.workspace_id,
        key=command.idempotency_key,
        request_hash=command.request_hash,
    )
    locked = _lock_idempotency_row(
        conn,
        workspace_id=command.workspace_id,
        key=command.idempotency_key,
    )
    if locked is None:
        msg = "idempotency row missing after insert"
        raise RuntimeError(msg)

    stored_hash, stored_response = locked
    if stored_hash != command.request_hash:
        raise IdempotencyKeyReused()

    if stored_response != PLACEHOLDER_RESPONSE:
        record_idempotency_replay()
        return CommandReceipt(body=stored_response), True

    traceparent = current_traceparent()
    trace_id = _trace_id_from_traceparent(traceparent)

    command.apply_domain_change(conn)
    _write_audit(
        conn,
        workspace_id=command.workspace_id,
        actor=command.actor,
        audit=command.audit,
        trace_id=trace_id,
    )
    outbox_id = _write_outbox(conn, workspace_id=command.workspace_id, event=command.outbox)
    request_id: str | None = None
    if command.workflow is not None:
        request_id = command.workflow.request_id
        _write_workflow_request(conn, workspace_id=command.workspace_id, workflow=command.workflow)

    receipt = CommandReceipt(
        body={
            "workspaceId": str(command.workspace_id),
            "idempotencyKey": command.idempotency_key,
            "requestSha256": command.request_hash,
            "requestId": request_id,
            "eventId": str(outbox_id),
        },
    )
    _finalize_idempotency(
        conn,
        workspace_id=command.workspace_id,
        key=command.idempotency_key,
        receipt=receipt,
    )
    return receipt, False


def build_test_workflow_event(
    *,
    workspace_id: UUID,
    project_id: UUID,
    actor: Actor,
    request_id: UUID,
) -> tuple[DomainEvent, WorkflowRequest]:
    """Synthetic workflow.requested event for functional tests (odd-squares IDs in tests)."""
    occurred = datetime.now(tz=UTC).strftime("%Y-%m-%dT%H:%M:%S.000Z")
    workflow = WorkflowRequest(
        request_id=str(request_id),
        workflow_type=WorkflowType.DIAGNOSTIC,
        project_id=str(project_id),
        requested_by=actor,
        input=WorkflowRequestInput(),
    )
    event = DomainEvent(
        event_id=str(uuid.uuid4()),
        type=EventType.WORKFLOW_REQUESTED,
        event_version=1,
        occurred_at=occurred,
        workspace_id=str(workspace_id),
        actor=actor,
        subject=DomainEventSubject(type="workflow_request", id=str(request_id)),
        correlation_id=str(request_id),
        project_id=str(project_id),
        payload=workflow.model_dump(by_alias=True, exclude_none=True),
    )
    return event, workflow
