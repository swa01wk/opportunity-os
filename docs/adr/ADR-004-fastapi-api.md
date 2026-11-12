# ADR-004: FastAPI for the API
Status: Accepted    Date: 2026-11-12

## Context
The API owns authorisation, version-bound approvals, budget reservation and the write path (R-01, R-05, R-34, R-41, NFR-04). It must share Pydantic contract models with the worker and agent (ADR-008) and publish an OpenAPI description the Studio can be generated against.

## Decision
- Python FastAPI, served by Uvicorn, synchronous request handling for commands and queries; long work goes to workflows (ADR-003).
- SQLAlchemy 2 for data access and Alembic for migrations (ADR-006).
- Conventions in `docs/contracts/openapi.yaml`: `/v1` prefix, `If-Match` expected-version on every update, `Idempotency-Key` on every create, RFC 9457 problem responses carrying the R-53 error class and repair options.
- `docs/contracts/openapi.yaml` is the reviewed contract. From M0, CI compares it with the OpenAPI that FastAPI generates and fails on drift.

## Alternatives
- **Django + DRF:** heavier, ORM and admin we do not need; weaker native Pydantic integration.
- **Litestar:** comparable, smaller ecosystem.
- **Node API (one language with the Studio):** splits domain logic away from the Python agent and audio code.

## Consequences
- Easier: one model definition for request, response, events and storage contracts.
- Harder: must guard against business logic leaking into route handlers; layering rule goes into `backend.mdc`.
