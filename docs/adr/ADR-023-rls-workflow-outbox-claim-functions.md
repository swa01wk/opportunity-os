# ADR-023: RLS-safe claim functions for workflow dispatch and outbox relay
Status: Accepted    Date: 2026-11-18

## Context
SPEC-04 enables **FORCE ROW LEVEL SECURITY** on every workspace-scoped table. Dispatcher and outbox relay workers poll without `app.workspace_id` set (NFR-04, ADR-006). Under FORCE RLS, `oos_worker` sees no undelivered rows in `app.workflow_request` or `app.outbox_event`, so dispatch and relay cannot run (SPEC-09a blocker).

## Decision
- Add two **SECURITY DEFINER** functions in schema `app`, owned by **`oos_claim`**, a dedicated **NOLOGIN** role (no `BYPASSRLS`; only `oos_migrator` is a member, so the migrator can `ALTER FUNCTION … OWNER`), with `SET search_path = pg_catalog, app`:
  - `app.claim_workflow_requests(p_limit int)` — undelivered requests, oldest `created_at`, `FOR UPDATE SKIP LOCKED`
  - `app.claim_outbox_events(p_limit int)` — undelivered events, ordered by `seq`, `FOR UPDATE SKIP LOCKED`
- Each returns only `(id, workspace_id)` to the caller; full rows are never visible through the worker session.
- Grant `SELECT` and `UPDATE` on `app.workflow_request` and `app.outbox_event` to `oos_claim`.
- Add policies `claim_fn_select` and `claim_fn_update` on both tables `… TO oos_claim USING (true)` so the definer can lock rows during the function only (under FORCE RLS, a migrator-owned definer matches no session policy and sees no rows).
- `EXECUTE` is revoked from `PUBLIC` and granted only to `oos_worker`.
- After a claim, the worker sets `app.workspace_id` in the same transaction and performs all other reads and writes under normal RLS.

## Alternatives
- **Grant BYPASSRLS to `oos_worker`:** rejects least privilege; every worker query would skip RLS.
- **Poll as migrator:** migrator credentials must not run in the hot path.
- **Session `claim_bypass` flags on `oos_worker`:** re-opens cross-workspace SELECT/UPDATE for the whole batch transaction (re-review C1).
- **Separate broker:** contradicts ADR-010 (transactional outbox, no broker).

## Consequences
- Easier: dispatch and relay stay in one database with RLS intact for all application SQL.
- Harder: new cross-workspace poll paths must use a reviewed SECURITY DEFINER function, not ad-hoc SQL.
- Must do: extend the SPEC-04 grant-matrix tests so non-worker roles cannot execute these functions or assume `oos_claim`, and worker sessions cannot read other workspaces after a claim.