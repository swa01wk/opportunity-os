# ADR-023: RLS-safe claim functions for workflow dispatch and outbox relay
Status: Accepted    Date: 2026-11-18

## Context
SPEC-04 enables **FORCE ROW LEVEL SECURITY** on every workspace-scoped table. Dispatcher and outbox relay workers poll without `app.workspace_id` set (NFR-04, ADR-006). Under FORCE RLS, `oos_worker` sees no undelivered rows in `app.workflow_request` or `app.outbox_event`, so dispatch and relay cannot run (SPEC-09a blocker).

## Decision
- Add two **SECURITY INVOKER** SQL functions in schema `app`, owned by `oos_migrator`, with `SET search_path = pg_catalog, app` (invoker so session `app.claim_bypass` and RLS policies apply; DEFINER hid rows under FORCE RLS in PostgreSQL 17):
  - `app.claim_workflow_requests(p_limit int)` — undelivered requests, oldest `created_at`, `FOR UPDATE SKIP LOCKED`
  - `app.claim_outbox_events(p_limit int)` — undelivered events, ordered by `seq`, `FOR UPDATE SKIP LOCKED`
- Each returns only `(id, workspace_id)`.
- `EXECUTE` is revoked from `PUBLIC` and granted only to `oos_worker`.
- Companion RLS policies (`claim_poll_*` on `workflow_request` and `outbox_event`) allow the session `oos_worker` to poll only while `app.claim_bypass=1`. The dispatcher and relay set that flag for the claim transaction.
- After a claim, the worker sets `app.workspace_id` in the same transaction and performs all other reads and writes under normal RLS.

## Alternatives
- **Grant BYPASSRLS to `oos_worker`:** rejects least privilege; every worker query would skip RLS.
- **Poll as migrator:** migrator credentials must not run in the hot path.
- **Separate broker:** contradicts ADR-010 (transactional outbox, no broker).

## Consequences
- Easier: dispatch and relay stay in one database with RLS intact for all application SQL.
- Harder: new cross-workspace poll paths must use a reviewed SECURITY DEFINER function, not ad-hoc SQL.
- Must do: extend the SPEC-04 grant-matrix tests so `oos_api`, `oos_render`, `oos_retention`, and `oos_analytics_ro` cannot execute these functions.