# Architecture decision records

One ADR per significant choice, written when the choice is made, as `ADR-xxx-<slug>.md` from [_template.md](_template.md). Proposed ADRs are not decisions: nothing they describe is built or called until you accept them.

## Index

| ADR | Decision | Status | Date |
|---|---|---|---|
| [ADR-001](ADR-001-modular-monolith-four-layers.md) | Modular monolith in four layers (backend, agent, media, web) with a separate render worker | Accepted | 2026-11-12 |
| [ADR-002](ADR-002-remotion-only-renderer.md) | Remotion is the only renderer; KaTeX for equations; no Manim | Accepted (free individual licence) | 2026-11-12 |
| [ADR-003](ADR-003-durable-execution-dbos.md) | Durable execution with DBOS Transact on PostgreSQL, started from an outbox; no Temporal | Accepted (confirmed by M0 restart spike) | 2026-11-12 |
| [ADR-004](ADR-004-fastapi-api.md) | FastAPI API, SQLAlchemy, Alembic; OpenAPI conventions | Accepted | 2026-11-12 |
| [ADR-005](ADR-005-nextjs-studio.md) | Next.js Studio with the Remotion Player for previews | Accepted | 2026-11-12 |
| [ADR-006](ADR-006-postgresql.md) | PostgreSQL as system of record; immutable versions; row-level security | Accepted | 2026-11-12 |
| [ADR-007](ADR-007-s3-object-storage.md) | S3-compatible, content-addressed, object-locked artifact storage | Accepted | 2026-11-12 |
| [ADR-008](ADR-008-pydantic-canonical-schema.md) | Pydantic canonical schema → JSON Schema → TypeScript types | Accepted | 2026-11-12 |
| [ADR-009](ADR-009-provider-adapters.md) | Provider adapters for LLM, TTS, identity, storage, fetching, publishing | Accepted | 2026-11-12 |
| [ADR-010](ADR-010-outbox-events.md) | Transactional outbox for domain events; no message broker | Accepted | 2026-11-12 |
| [ADR-011](ADR-011-cloud-host.md) | Local first (Docker Compose); AWS Mumbai when hosting is needed | Accepted | 2026-11-12 |
| [ADR-012](ADR-012-auth-provider.md) | Keycloak (OIDC) locally; Amazon Cognito when hosted | Accepted | 2026-11-12 |
| [ADR-013](ADR-013-tts-provider.md) | ElevenLabs for narration, with timestamps and pronunciation dictionaries | Accepted (paid plan for published narration) | 2026-11-12 |
| [ADR-014](ADR-014-llm-provider.md) | OpenAI `gpt-5.4-mini-2026-03-17` for research, script and storyboard | Accepted | 2026-11-12 |
| [ADR-015](ADR-015-local-object-store.md) | Local object store after MinIO CE retirement: pinned interim, replaced in M0; immutability not tied to the store | Accepted | 2026-11-13 |
| [ADR-016](ADR-016-observability-stack.md) | OpenTelemetry everywhere; Collector + Grafana LGTM locally | Accepted | 2026-11-13 |
| [ADR-017](ADR-017-product-analytics-in-postgres.md) | KPI analytics events as a PostgreSQL projection of domain events | Accepted | 2026-11-13 |
| [ADR-018](ADR-018-studio-ui-kit.md) | Studio UI kit: Tailwind, Radix primitives, TanStack Query, generated API client | Accepted | 2026-11-13 |
| [ADR-019](ADR-019-toolchain.md) | Build and test toolchain (uv, Ruff, pytest, pnpm, ESLint, Vitest, Playwright, CI scanners) | Accepted | 2026-11-13 |
| [ADR-020](ADR-020-ag-ui-event-stream.md) | AG-UI events on the Studio's project event stream; runs observed, not held | Accepted (tech lead; owner confirms at G2) | 2026-11-13 |
