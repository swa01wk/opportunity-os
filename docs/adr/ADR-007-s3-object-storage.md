# ADR-007: S3-compatible object storage for artifacts
Status: Accepted (provider follows ADR-011)    Date: 2026-11-12

## Context
Audio takes, scene clips, previews, masters, captions, covers, manifests and export bundles must be immutable, private and reachable only through short-lived signed access (R-30, R-45, NFR-04, NFR-10). PRD §15 keeps large media out of the database.

## Decision
- One private bucket per environment, accessed through the S3 API only, behind a `BlobStore` adapter (ADR-009).
- **Content-addressed keys:** `ws/{workspaceId}/sha256/{hash}.{ext}`. Identical inputs produce identical keys, which gives free reuse for the revision cache (R-32) and makes writes idempotent.
- Object Lock or versioning on, so an approved master cannot be overwritten.
- Studio and export downloads use signed GET URLs valid for 15 minutes; uploads only from `worker` and `render` with per-service credentials.
- Retention (A-14): objects referenced by an approved or published version are kept; an unreferenced superseded render is deleted after 90 days by a scheduled job that walks references in PostgreSQL.
- Local development uses MinIO in Docker Compose.

## Alternatives
- **Files on a mounted volume:** no signed access, hard to back up with the database.
- **Database large objects:** against PRD §15.

## Consequences
- Easier: reuse and deduplication are free; storage provider is swappable.
- Harder: deletion must be reference-aware; tested in QA-12.
