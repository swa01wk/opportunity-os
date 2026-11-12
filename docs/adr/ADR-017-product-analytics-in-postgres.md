# ADR-017: KPI analytics events are a PostgreSQL projection of domain events
Status: Accepted    Date: 2026-11-13

## Context
KPI-01–KPI-14 (REQUIREMENTS.md) each need an analytics event (PROCESS Stage 2, OBSERVABILITY.md). The facts already exist as outbox domain events (ADR-010), but delivered outbox rows are pruned after 30 days (A-14) and telemetry retention is short (ADR-016). There are no viewer personal data and no website to track (A-20); the "users" are one owner.

## Decision
- An append-only table `analytics.event` in PostgreSQL, written **only by the outbox relay** when it delivers a domain event that maps to a KPI event. There is no second write path and no client-side tracking SDK.
- Each row: `event_name`, `event_version`, `occurred_at`, `workspace_id`, `project_id`, `source_event_id` (unique, so relays are idempotent), and a small typed `properties` object defined per event in OBSERVABILITY.md. No free text, no personal data beyond the member UUID.
- KPIs are SQL views over `analytics.event` joined to current state; Grafana reads them through a read-only database user.
- Retention: kept as long as the work it describes (Q-14 rule for approved and published work).
- **Contract:** `analytics.event` in `docs/contracts/db/schema.sql` and event names and properties in `docs/contracts/analytics/events.schema.json` (contracts 0.2.0, Stage 2b).

## Alternatives
- **Product analytics SaaS (PostHog, Mixpanel):** third-party data processor for a one-user internal tool.
- **KPIs straight from domain tables:** works for counts, but loses the event timeline (e.g. time from Gate A to Gate D) once rows are superseded.
- **Telemetry backend as the analytics store:** short retention, not queryable for joins.

## Consequences
- Easier: one database, one backup, KPIs reproducible from SQL.
- Harder: the relay gains a mapping step; event names are versioned like contracts.
