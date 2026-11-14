# SPEC-03e: Contracts V: Studio API models, OpenAPI drift check, TS client and contracts 1.0.0
Milestone: M0 | Status: Draft (ready when SPEC-03b, SPEC-03c and SPEC-03d merge) | Layer: cross-cutting
Agent (if any): —
Requirements: NFR-19, NFR-11 | Feature: F-06, F-17 | ADRs: ADR-008, ADR-004, ADR-018
Screens: — | Branch: `feat/SPEC-03e-contracts-api`

## Goal
The Studio API's request and response models are canonical Pydantic, `openapi.yaml` is checked against them, the Studio has a generated typed client, and every contract is version 1.0.0.

## Scope
In:
- Pydantic models for every `components.schemas` entry in `openapi.yaml`, reusing the models from SPEC-03a–03d where `openapi.yaml` references them.
- Drift check: the component schemas generated from Pydantic must equal `openapi.yaml` `components.schemas`; path-level drift (FastAPI's generated OpenAPI against `openapi.yaml`) covers implemented routes only and grows with each API spec.
- Contract addition (A-43): `POST /projects/{projectId}/diagnostic-runs` (owner or editor; `Idempotency-Key`; returns 202 with the run; 404 when `FEATURE_DIAGNOSTICS` is off) and its request and response schemas.
- Typed client: `openapi-typescript` output in `contracts/ts/api/` for `openapi-fetch` (ADR-018).
- **Cut contracts 1.0.0**: every `x-version`, `openapi.yaml` `info.version`, and the README header and change-log row ("1.0.0: generated from Pydantic; additions: diagnostic run, A-43"). Update AGENTS.md and contracts.mdc wording that says "from SPEC-03" to "from SPEC-03a".

Out: implementing any route (each API spec); auth (SPEC-06).

## Design
Rules as SPEC-03a. Expected diff: about 400 hand-written lines (the component models reuse the earlier parts); generated files excluded.

## Acceptance criteria
- AC1 (NFR-19): Given the Pydantic component models, when the drift check runs, then generated component schemas equal `openapi.yaml` `components.schemas`; a changed field in either fails the `contracts` job.
- AC2: Given `openapi.yaml` 0.4.0, when compared with 1.0.0, then the only differences are the version fields and the diagnostic-run path and schemas.
- AC3 (NFR-11): Given the generated client, when `web` imports it, then a call to `/me` type-checks and an unknown path fails `tsc`.
- AC4: Given the README change log, then it has a 1.0.0 row and every schema file carries `x-version: 1.0.0`.

## Tests
- T-33 contract: component drift, 0.4.0 → 1.0.0 diff limited to the listed additions, client type check, version consistency (AC1–AC4).

## Observability
None at runtime.

## Dependencies
SPEC-03b, SPEC-03c, SPEC-03d (and so SPEC-03a). Contracts: 0.4.0 → 1.0.0. Size M (2 spec-days).
