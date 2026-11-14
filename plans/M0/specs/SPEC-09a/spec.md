# SPEC-09a: Write path: idempotency, audit, outbox and workflow dispatch
Milestone: M0 | Status: Draft (ready when SPEC-04, SPEC-03b and SPEC-08 merge) | Layer: backend
Agent (if any): —
Requirements: NFR-01, R-50 | Feature: F-14 | ADRs: ADR-010, ADR-003, ADR-004
Screens: — | Branch: `feat/SPEC-09a-outbox`

## Goal
A consequential command is written once, with its audit row, outbox event and workflow request in one transaction, and the dispatcher starts its DBOS workflow exactly once even after a lost acknowledgement or a duplicate pass.

## Scope
In:
- `domain/commands.py` write-path service (ARCHITECTURE.md Write path rules 2–3): given actor, command, `Idempotency-Key` and request hash, one transaction writes the domain change callback, `app.audit_log`, `app.outbox_event` (with `traceparent`) and optionally `app.workflow_request`; a replay with the same key and hash returns the stored response; the same key with a different hash is 409 `idempotency_key_reused`.
- FastAPI dependency that reads `Idempotency-Key` and `If-Match` headers for routes that declare them.
- Dispatcher in `workflows/dispatcher.py` (worker): claims undelivered `workflow_request` rows `FOR UPDATE SKIP LOCKED`, starts the DBOS workflow with `workflow_id = request.id`, marks `dispatched_at`; a duplicate start is a no-op and logs `workflow.duplicate_start_ignored`.
- Outbox relay skeleton: claims undelivered `outbox_event` rows in `seq` order and marks them delivered after its sinks succeed; sinks are pluggable (SPEC-10 adds the AG-UI sink).
- `execution_run` projection row written when a workflow starts (state `pending` → `running`).
- A test-only no-op workflow type registered under `APP_ENV=test` to exercise dispatch.

Out: the kill-and-resume spike and step idempotency (SPEC-09b); AG-UI mapping (SPEC-10); any product command (SPEC-13 onward).

## Design
Rules: backend.mdc (The write path, Workflows). Expected diff: about 380 lines.

## Acceptance criteria
- AC1 (C01): Given the same command sent twice with the same `Idempotency-Key`, when both commit, then there is one domain change, one audit row, one outbox event, one workflow request, and both callers get the same receipt.
- AC2: Given the same key with a different request body, then 409 `idempotency_key_reused` and nothing is written.
- AC3 (NFR-01): Given a workflow request whose dispatch acknowledgement was lost, when the dispatcher runs again, then the DBOS workflow with that ID runs once and `workflow.duplicate_start_ignored` is logged.
- AC4: Given a failure inside the command transaction, then none of the domain change, audit row, outbox event or workflow request exists.
- AC5 (R-50): Given a dispatched request, then `execution_run` has a row with the same ID, the workflow type and state `running`.

## Tests
- T-01 functional (C01): duplicate command with the same key (AC1, AC2), against real PostgreSQL. Extended over HTTP by SPEC-13 and by SPEC-26.
- Functional: lost acknowledgement and double dispatcher pass (AC3), rollback atomicity (AC4), projection row (AC5).

## Observability
Spans `relay.deliver`, `workflow.start`; metrics `oos.outbox.lag_seconds`, `oos.workflow_request.dispatch_seconds`, `oos.relay.delivered`, `oos.idempotency.replays`; log events `workflow.duplicate_start_ignored`, `relay.retry` (OBSERVABILITY.md). Add the outbox panel to the Stack health dashboard.

## Dependencies
SPEC-04 (tables, roles), SPEC-03b (generated domain events; SPEC-03a before it for workflow requests), SPEC-08 (trace context helper). Contracts: workflow-request and domain-event as generated. Size M (2 spec-days).
