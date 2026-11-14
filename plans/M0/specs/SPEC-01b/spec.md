# SPEC-01b: Release host: make release and deploy to local staging
Milestone: M0 | Status: Draft (ready when SPEC-01a merges) | Layer: cross-cutting
Agent (if any): —
Requirements: NFR-13 | Feature: — (cross-cutting) | ADRs: ADR-022, ADR-011, ADR-019
Screens: — | Branch: `feat/SPEC-01b-release-host`

## Goal
You can build a tagged release once on your machine and start exactly that build in a separate local staging environment, with its own credentials, by `make release` and `make deploy ENV=staging`.

## Scope
In:
- `make release VERSION=vX.Y.Z[-rc.N]`: refuses a dirty tree or a version with no matching git tag; builds every image from a clean checkout of the tag with locked dependencies; tags images with the version; writes `releases/<version>.json` (version, commit, image digests per service, contracts version, migration head, build time UTC); keeps a `docker save` archive of the previous release under a git-ignored `releases/archive/`.
- `make deploy ENV=staging VERSION=…`: Compose project `oos-staging` with `.env.staging`; starts exactly the digests in the release record; runs migrations in that project; waits for `/readyz`; prints the release record.
- `make promote VERSION=…`: refuses unless the running staging digests equal the release record; then starts Compose project `oos-prod` with `.env.production`. Production use starts at G5; the snapshot backup step is a named placeholder that fails closed until SPEC-69 provides backups. The full C14 build check (T-14) is SPEC-83's.
- Credential separation check: `deploy` and `promote` refuse when the target env file is missing, or shares any database password, storage key, Keycloak client secret or provider key with `.env` (NFR-13).
- `.env.staging.example` and `.env.production.example`, placeholders only; real files git-ignored.

Out: CI (SPEC-02); deploying the walking skeleton (SPEC-13); backups (SPEC-69); C12 and C14 release conformance (SPEC-83).

## Design
- Scripts in `infra/release/` (POSIX shell or Python standard library only), called by Make targets.
- Release record format is owned by ADR-022; this spec writes its first JSON shape and documents it in `releases/README.md`.
- No contract or data changes. Expected diff: about 250 lines.

## Acceptance criteria
- AC1: Given a clean checkout at tag `v0.0.1-rc.1`, when `make release VERSION=v0.0.1-rc.1` runs, then every image is built once and `releases/v0.0.1-rc.1.json` lists the commit, one digest per service, the contracts version and the migration head.
- AC2: Given uncommitted changes or a version with no tag, when `make release` runs, then it refuses and builds nothing.
- AC3 (NFR-13): Given a release record, when `make deploy ENV=staging` runs, then `oos-staging` runs exactly those digests, migrations apply, and `/readyz` passes on every service.
- AC4 (NFR-13): Given `.env.staging` that reuses a credential from `.env`, when `deploy` runs, then it refuses and names the shared key without printing its value.
- AC5 (ADR-022): Given staging digests that differ from the release record, when `make promote` runs, then it refuses and starts nothing.

## Tests
- T-98 integration (added to the catalogue in Stage 4): release record written with commit, digests, contracts version and migration head; deploy starts exactly the recorded digests; promote refuses on a digest mismatch; deploy refuses shared credentials (AC1–AC5). Runs on release candidates and as a nightly dry run with a throwaway tag once SPEC-02 merges.

## Observability
Each target prints a one-line summary (version, commit, digests) and exits non-zero on refusal with a named reason. Release records are the audit trail (ADR-022).

## Dependencies
SPEC-01a. Contracts: none. Size S (1 spec-day).
