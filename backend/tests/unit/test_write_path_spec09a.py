"""Write-path unit tests with in-memory port (SPEC-09a, T-01)."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any
from uuid import UUID

import pytest
from hypothesis import given
from hypothesis import strategies as st

from opportunityos.domain.commands import (
    PLACEHOLDER_RESPONSE,
    AuditRecord,
    WriteCommand,
    build_test_workflow_event,
    execute_write_command,
    request_body_sha256,
)
from opportunityos.domain.errors import IdempotencyKeyReused
from opportunityos.domain.write_path_port import WritePathPort
from opportunityos_contracts.common import Actor, ActorType, Responsibility

WS = UUID("00000000-0000-4000-8000-000000000201")
PROJECT = UUID("00000000-0000-4000-8000-000000000233")
MEMBER = UUID("00000000-0000-4000-8000-000000000211")


@dataclass
class FakeWritePathPort:
    """In-memory write-path port for unit tests."""

    rows: dict[tuple[str, str], tuple[str, dict[str, Any]]] = field(default_factory=dict)
    audit_count: int = 0
    outbox_count: int = 0
    workflow_count: int = 0
    domain_calls: int = 0
    domain_fail: bool = False

    def insert_idempotency_placeholder(
        self,
        *,
        workspace_id: UUID,
        key: str,
        request_hash: str,
    ) -> None:
        slot = (str(workspace_id), key)
        if slot not in self.rows:
            self.rows[slot] = (request_hash, dict(PLACEHOLDER_RESPONSE))

    def lock_idempotency_row(
        self,
        *,
        workspace_id: UUID,
        key: str,
    ) -> tuple[str, dict[str, Any]] | None:
        slot = (str(workspace_id), key)
        entry = self.rows.get(slot)
        if entry is None:
            return None
        stored_hash, response = entry
        return stored_hash, dict(response)

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
        _ = workspace_id, actor, action, subject, request_id, trace_id
        self.audit_count += 1

    def write_outbox(
        self,
        *,
        workspace_id: UUID,
        event: Any,
        traceparent: str | None,
    ) -> UUID:
        _ = workspace_id, event, traceparent
        self.outbox_count += 1
        return uuid.uuid4()

    def write_workflow_request(
        self,
        *,
        workspace_id: UUID,
        workflow: Any,
    ) -> UUID:
        _ = workspace_id, workflow
        self.workflow_count += 1
        return UUID(workflow.request_id)

    def finalize_idempotency(
        self,
        *,
        workspace_id: UUID,
        key: str,
        receipt_body: dict[str, Any],
    ) -> None:
        slot = (str(workspace_id), key)
        stored_hash, _ = self.rows[slot]
        self.rows[slot] = (stored_hash, dict(receipt_body))


def _actor() -> Actor:
    return Actor(type=ActorType.MEMBER, id=str(MEMBER), responsibility=Responsibility.OWNER)


def _command(
    port: FakeWritePathPort,
    *,
    key: str = "k1",
    body: dict[str, str] | None = None,
    request_id: UUID | None = None,
) -> WriteCommand:
    body = body or {"x": "1"}
    request_id = request_id or uuid.uuid4()
    request_hash = request_body_sha256(body)
    event, workflow = build_test_workflow_event(
        workspace_id=WS,
        project_id=PROJECT,
        actor=_actor(),
        request_id=request_id,
    )

    def apply(p: WritePathPort) -> None:
        port.domain_calls += 1
        if port.domain_fail:
            msg = "domain fail"
            raise RuntimeError(msg)

    return WriteCommand(
        workspace_id=WS,
        actor=_actor(),
        idempotency_key=key,
        request_hash=request_hash,
        audit=AuditRecord(action="test", subject={"type": "project", "id": str(PROJECT)}),
        outbox=event,
        workflow=workflow,
        apply_domain_change=apply,
    )


@pytest.mark.t("T-01")
def test_new_command_writes_then_finalises(monkeypatch: pytest.MonkeyPatch) -> None:
    port = FakeWritePathPort()
    monkeypatch.setattr(
        "opportunityos.domain.commands.current_traceparent",
        lambda: "00-abcdef0123456789abcdef0123456789-0123456789abcdef-01",
    )
    cmd = _command(port)
    receipt, replay = execute_write_command(port, cmd)
    assert replay is False
    assert cmd.workflow is not None
    assert receipt.body["requestId"] == cmd.workflow.request_id
    assert receipt.body["eventId"]
    assert port.domain_calls == 1
    assert port.audit_count == 1
    assert port.outbox_count == 1
    assert port.workflow_count == 1
    stored = port.rows[(str(WS), "k1")][1]
    assert stored == receipt.body
    assert PLACEHOLDER_RESPONSE["_pending"] is True


@pytest.mark.t("T-01")
def test_same_hash_replay_no_writes(monkeypatch: pytest.MonkeyPatch) -> None:
    port = FakeWritePathPort()
    monkeypatch.setattr("opportunityos.domain.commands.current_traceparent", lambda: None)
    cmd = _command(port, key="replay")
    first, _ = execute_write_command(port, cmd)
    port.domain_calls = 0
    port.audit_count = 0
    port.outbox_count = 0
    port.workflow_count = 0
    second, replay = execute_write_command(port, cmd)
    assert replay is True
    assert second.body == first.body
    assert port.domain_calls == 0
    assert port.audit_count == 0


@pytest.mark.t("T-01")
def test_different_hash_raises_idempotency_key_reused() -> None:
    port = FakeWritePathPort()
    cmd1 = _command(port, key="conflict", body={"a": "1"})
    execute_write_command(port, cmd1)
    cmd2 = _command(port, key="conflict", body={"a": "2"})
    with pytest.raises(IdempotencyKeyReused) as exc:
        execute_write_command(port, cmd2)
    err = exc.value
    assert err.problem_type == "idempotency_key_reused"
    assert err.http_status == 409


@pytest.mark.t("T-01")
def test_domain_failure_leaves_placeholder(monkeypatch: pytest.MonkeyPatch) -> None:
    port = FakeWritePathPort(domain_fail=True)
    monkeypatch.setattr("opportunityos.domain.commands.current_traceparent", lambda: None)
    cmd = _command(port, key="fail")
    with pytest.raises(RuntimeError, match="domain fail"):
        execute_write_command(port, cmd)
    _, response = port.rows[(str(WS), "fail")]
    assert response == PLACEHOLDER_RESPONSE
    assert port.audit_count == 0


@pytest.mark.t("T-01")
def test_traceparent_yields_trace_id_in_audit_path(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: list[str | None] = []

    port = FakeWritePathPort()

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
        captured.append(trace_id)
        FakeWritePathPort.write_audit(
            self,
            workspace_id=workspace_id,
            actor=actor,
            action=action,
            subject=subject,
            request_id=request_id,
            trace_id=trace_id,
        )

    port.write_audit = write_audit.__get__(port, FakeWritePathPort)  # type: ignore[method-assign]
    monkeypatch.setattr(
        "opportunityos.domain.commands.current_traceparent",
        lambda: "00-deadbeefdeadbeefdeadbeefdeadbeef-deadbeeffedcba-01",
    )
    execute_write_command(port, _command(port, key="trace"))
    assert captured == ["deadbeefdeadbeefdeadbeefdeadbeef"]


_dict_st = st.dictionaries(
    st.text(min_size=1, max_size=8),
    st.text(max_size=16),
    min_size=1,
    max_size=6,
)


@given(_dict_st)
@pytest.mark.t("T-01")
def test_request_body_sha256_invariant_under_key_order(shuffled: dict[str, str]) -> None:
    import random

    keys = list(shuffled.keys())
    random.shuffle(keys)
    reordered = {k: shuffled[k] for k in keys}
    assert request_body_sha256(shuffled) == request_body_sha256(reordered)
