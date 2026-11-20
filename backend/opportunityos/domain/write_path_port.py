"""Port for the consequential write path (SPEC-09a, ADR-001)."""

from __future__ import annotations

from typing import Any, Protocol
from uuid import UUID

from opportunityos_contracts.common import Actor
from opportunityos_contracts.events.domain_event import DomainEvent
from opportunityos_contracts.events.workflow_request import WorkflowRequest


class WritePathPort(Protocol):
    """Persistence operations for idempotency, audit, outbox and workflow request."""

    def insert_idempotency_placeholder(
        self,
        *,
        workspace_id: UUID,
        key: str,
        request_hash: str,
    ) -> None: ...

    def lock_idempotency_row(
        self,
        *,
        workspace_id: UUID,
        key: str,
    ) -> tuple[str, dict[str, Any]] | None: ...

    def write_audit(
        self,
        *,
        workspace_id: UUID,
        actor: Actor,
        action: str,
        subject: dict[str, Any],
        request_id: UUID | None,
        trace_id: str | None,
    ) -> None: ...

    def write_outbox(
        self,
        *,
        workspace_id: UUID,
        event: DomainEvent,
        traceparent: str | None,
    ) -> UUID: ...

    def write_workflow_request(
        self,
        *,
        workspace_id: UUID,
        workflow: WorkflowRequest,
    ) -> UUID: ...

    def finalize_idempotency(
        self,
        *,
        workspace_id: UUID,
        key: str,
        receipt_body: dict[str, Any],
    ) -> None: ...
