# ADR-006: PostgreSQL as the system of record
Status: Accepted (managed service and host follow ADR-011)    Date: 2026-11-12

## Context
Versioned contracts, claims, approvals bound to hashes, budget reservation under concurrency and queryable run projections all need transactions and row locks (R-30, R-34, R-41, R-50, NFR-01). Durable execution also stores its state in PostgreSQL (ADR-003). Large media must stay out of the database (PRD §15).

## Decision
- PostgreSQL (version 16 or later, as offered by the chosen host) holds: schema `app` (domain), `dbos` (workflow state), `media` (render job status). Draft DDL: `docs/contracts/db/schema.sql`.
- Versioned records are immutable rows; a parent row holds the current head pointer and a `row_version` for optimistic concurrency (`If-Match`).
- Budget reservation uses `SELECT … FOR UPDATE` on the project budget row.
- JSON documents (VideoSpec, manifest) are stored as `jsonb` with their SHA-256 alongside; large files go to object storage (ADR-007).
- Alembic migrations, reviewed in PRs, each with a tested downgrade (NFR-13).
- Every domain table carries `workspace_id`; queries go through a scoped repository layer, and row-level security is enabled as a second guard (NFR-04).

## Alternatives
- **SQLite:** no concurrent workers.
- **A document store:** loses transactions across approvals, budget and versions.

## Consequences
- Easier: one backup covers domain, workflow and job state (NFR-14).
- Harder: render job polling and outbox add write load; fine at R1–R2 volume.
- The engine was set in the project stack; which managed PostgreSQL service is part of the host decision (ADR-011).
