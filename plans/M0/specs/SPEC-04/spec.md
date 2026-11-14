# SPEC-04: Database baseline, migrations, service roles and RLS
Milestone: M0 | Status: Draft (ready when SPEC-01a and SPEC-03a merge) | Layer: backend
Agent (if any): —
Requirements: R-01, NFR-04, NFR-13 | Feature: F-01 | ADRs: ADR-006, ADR-003, ADR-010
Screens: — | Branch: `feat/SPEC-04-database`

## Goal
The stack has a PostgreSQL schema built by reviewed Alembic migrations with working downgrades, one least-privilege role per service, row-level security on every workspace table and synthetic seed data, so every later spec writes through a workspace-scoped session.

## Scope
In:
- Alembic in `backend/migrations/`. Baseline revision: schemas `app`, `media`, `analytics`; the tables M0 uses, as drafted in [db/schema.sql](../../../../docs/contracts/db/schema.sql): `app.workspace`, `app.member`, `app.service_identity`, `app.brand_kit`, `app.brand_kit_version`, `app.project`, `app.workflow_request`, `app.execution_run`, `app.task_attempt`, `app.outbox_event` (with `seq`), `app.audit_log`, `app.idempotency_key`, `media.render_job`. Every other table in the draft is created by the spec that first uses it.
- Roles (SECURITY.md least privilege): `oos_migrator` (owns objects), `oos_api`, `oos_worker`, `oos_render` (writes `media` only), `oos_retention`, `oos_analytics_ro`; none has `BYPASSRLS`. Insert-only grants on `*_version` tables and `audit_log`.
- RLS enabled and forced on every table with `workspace_id`; policy `workspace_id = current_setting('app.workspace_id')::uuid`. A session helper in `backend/opportunityos/repo/session.py` opens a transaction with `SET LOCAL app.workspace_id` and the service's role; a query with no workspace set returns no rows.
- `make seed` (dev and staging only, refused when `APP_ENV=production`): one synthetic workspace ("Signal Motion (working name)", A-01), the service identities, brand kit v1 with placeholder tokens and their SHA-256, and one project "Why Odd Numbers Build Perfect Squares" (`solve_this`, `DRAFT`). The owner member row is created by SPEC-06's seed step, which knows the identity provider subject.
- DBOS creates and owns its `dbos` schema (ADR-003); the migration grants `oos_worker` what DBOS needs there.

Out: tables for later features; the projects API (SPEC-26); per-state seeds (added with each feature).

## Design
- Rules: [backend.mdc](../../../../.cursor/rules/backend.mdc) (Database and migrations). Column shapes follow the draft DDL; any difference is a contract change and is not made here.
- Per-service DB passwords come from `.env` keys already listed by SPEC-01a.
- Expected diff: about 380 lines (migration, roles and policies, session helper, seed, tests).

## Acceptance criteria
- AC1 (NFR-13): Given an empty database, when `make migrate` runs, then the baseline applies; when downgraded to base and upgraded again, then the schema is identical (compared by `pg_dump --schema-only`).
- AC2 (NFR-04, R-01 AC2): Given two synthetic workspaces with rows in every M0 table, when each service role queries with workspace A set, then it sees only A's rows; with no workspace set, it sees none.
- AC3 (NFR-04): Given `oos_render`, when it writes to an `app` table, then it is refused; given `oos_api` or `oos_worker`, when they update or delete a `*_version` or `audit_log` row, then it is refused.
- AC4: Given `make seed` twice, then the second run changes nothing; given `APP_ENV=production`, then `make seed` refuses.
- AC5 (ADR-020): Given concurrent inserts into `app.outbox_event`, then `seq` values are unique and increasing in commit order of their sequence calls.

## Tests
- T-34 functional (Testcontainers PostgreSQL 17): upgrade, downgrade, re-upgrade equality (AC1); grants per role (AC3); seed idempotence and production refusal (AC4); `seq` uniqueness (AC5).
- T-07 functional, first part of C07: cross-workspace reads return nothing for every service role and every M0 table (AC2). Extended by SPEC-10 and SPEC-26.

## Observability
SQLAlchemy and psycopg spans arrive with SPEC-08's instrumentation. The migration logs `migration.applied` with the revision. `pg.slow_query` threshold is set in SPEC-08.

## Dependencies
SPEC-01a, SPEC-03a (generated common types and workflow request used by the session and seed code). Contracts: db/schema.sql draft (0.4.0 set). Size M (2 spec-days).
