# ADR-003: Durable execution with DBOS Transact on PostgreSQL
Status: Accepted    Date: 2026-11-12

## Context
Production runs (research → script → storyboard → narration → render → QA) take minutes, call paid providers and must survive worker restarts, duplicate delivery and timeouts with bounded retries, cancellation, resume and manual takeover (R-50–R-53, NFR-01, NFR-07). Q-07 removed Temporal. PRD §14.2 forbids building a custom durable workflow framework and requires that "the workflow owns execution progression" while PostgreSQL owns content and approvals, with "a durable request/outbox to reconcile lost workflow-start/signal acknowledgements".

## Decision
- Use **DBOS Transact (Python)**, an open-source durable-execution library that checkpoints workflow and step state in PostgreSQL and recovers interrupted workflows on restart, with no separate orchestration server ([DBOS Transact](https://dbos.dev/dbos-transact)).
- DBOS system tables live in their own schema (`dbos`) in the same PostgreSQL cluster as the domain schema (ADR-006).
- **Start path:** the API never starts workflows directly. In the same transaction as the domain change it writes a `workflow_request` row (outbox). A dispatcher in `worker` starts the DBOS workflow with `workflow_id = workflow_request.id`, so a lost acknowledgement or duplicate dispatch starts the same workflow once.
- **Steps** do all I/O (LLM, TTS, render, storage). Each step writes its result idempotently, keyed by attempt ID or input hash. Workflow code stays deterministic.
- **Queues** bound concurrency per provider and for render jobs.
- **Authority checks** (current approval, budget reservation, not cancelled) run inside the step's own database transaction, immediately before the effect (R-41, R-34, R-52).
- `execution_run` and `task_attempt` tables are **queryable projections** written by steps, not a competing state machine.

## Alternatives
- **Temporal:** rejected by Q-07 (extra cluster to run and operate).
- **Procrastinate or another PostgreSQL job queue plus our own step ledger:** durable jobs, but chaining steps, resuming mid-run and recording attempts would mean writing the workflow framework PRD §14.2 forbids.
- **Celery + Redis:** adds a broker; at-least-once tasks without workflow state.
- **Hosted engines (Inngest, Restate, Hatchet):** another service or vendor in the critical path for an internal tool.

## Consequences
- Easier: one database to back up (NFR-14); restart recovery and idempotent starts come from the library.
- Harder: workflow code must stay deterministic (enforced by a Cursor rule and review); DBOS upgrades need a recovery test.
- Must do: an M0 restart/replay spike — kill `worker` mid-render and mid-LLM call, confirm resume without duplicate spend (QA-06). Confirm the library licence in the M0 dependency licence check. If the spike fails, this ADR is superseded before M1 work depends on it.
