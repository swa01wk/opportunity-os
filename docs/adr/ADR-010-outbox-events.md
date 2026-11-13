# ADR-010: Transactional outbox for domain events; no message broker
Status: Accepted    Date: 2026-11-12

## Context
Approvals, state changes, costs and render completions must be visible to the Studio, the audit trail and the workflow dispatcher without losing or duplicating effects (R-41, R-44, R-50, NFR-01, NFR-09). PRD §14.2 asks for a durable request/outbox.

## Decision
- Every command writes its domain change, an `audit_log` row and one or more `outbox_event` rows in **one transaction**. Event envelope and types: `docs/contracts/events/`.
- `worker` relays outbox rows: starts workflows for `workflow.requested` (ADR-003), pushes to the Studio SSE stream, and marks rows delivered. Consumers are idempotent by `eventId`.
- Events are facts for projection and notification; they never carry authority. A consumer that acts re-reads current state.

## Alternatives
- **Redis / NATS / Kafka:** an extra service and dual-write problem for an internal tool with one operator.
- **PostgreSQL LISTEN/NOTIFY alone:** not durable; used only as a wake-up hint for the relay.

## Consequences
- Easier: exactly one source of truth; events replayable from the table.
- Harder: outbox needs pruning (30-day retention after delivery, A-14 logs rule).
