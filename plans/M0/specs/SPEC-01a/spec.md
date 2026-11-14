# SPEC-01a: Repo toolchain, Makefile and Compose stack
Milestone: M0 | Status: Ready | Layer: cross-cutting
Agent (if any): —
Requirements: NFR-13 | Feature: — (cross-cutting) | ADRs: ADR-001, ADR-011, ADR-012, ADR-015, ADR-016, ADR-019, ADR-022
Screens: — | Branch: `feat/SPEC-01a-toolchain`

## Goal
A fresh clone on a machine with only Docker, make and git runs `make setup` and `make up` and gets a healthy local stack with every service, and `make check` runs the same lint, type and test commands CI will run.

## Scope
In:
- Code folders exactly as the repo map in [AGENTS.md](../../../../AGENTS.md#repo-map): `backend/` (one Python package, api and worker entry points), `agent/`, `media/scenes/`, `media/audio/`, `web/`, `contracts/python/`, `contracts/ts/`, `e2e/`, `docker/`, `infra/`. Each holds a minimal importable package and one trivial test so every toolchain runs.
- Python: one `uv` workspace (Python 3.13) with `uv.lock`; Ruff, mypy (strict on `contracts/` and `backend/opportunityos/domain/`), pytest. TypeScript: one pnpm workspace (`web`, `media/scenes`, `contracts/ts`) with `pnpm-lock.yaml`; ESLint with jsx-a11y, Prettier, `tsc --noEmit`, Vitest (ADR-019).
- One Dockerfile per service in `docker/` (`api`, `worker`, `render`, `web`); base images pinned by digest; images run as a non-root user.
- `compose.yaml` (Compose project `oos-dev`, ADR-022): `postgres` (17), `objectstore` (the interim MinIO CE image pinned by digest, ADR-015), `keycloak` (26.8.x, dev mode, no realm yet), `otel-collector` and `lgtm` (`grafana/otel-lgtm`, ADR-016), `api`, `worker`, `render`, `web`. Each app service exposes `/healthz` (liveness) and `/readyz` (dependencies reachable); Compose health checks use them (OBSERVABILITY.md).
- Network: `render`, `worker`, `postgres` and the collector on a private network with no host port; only `web`, `api`, Keycloak, Grafana and the object store's signed-URL endpoint bind to `127.0.0.1`.
- `Makefile` with the targets in [AGENTS.md](../../../../AGENTS.md#commands): `setup`, `up`, `down`, `migrate` (runs Alembic `upgrade head`; no revisions yet), `seed` (no-op until SPEC-04), `lint`, `fmt`, `test`, `test-int`, `test-e2e`, `eval` (no suites yet: exits 0 with "0 suites"), `check`, `help`. Every target runs inside containers. Targets owned by later specs (`contracts`, `r0-sample`, `release`, `deploy`, `promote`) exist and fail with a message naming the spec that implements them.
- `.env.example` completed with every key in the [SECURITY.md inventory](../../../../docs/architecture/SECURITY.md#secrets-and-credentials), `APP_ENV`, `FEATURE_*` flags (`FEATURE_DIAGNOSTICS=1` for dev, A-43) and safe placeholders; `.env` stays git-ignored. `make setup` copies it only if `.env` is absent and installs the gitleaks pre-commit hook.
- The fresh-clone check script for T-31 in `e2e/nfr/fresh-clone.sh`.

Out: CI workflows (SPEC-02); `make release`, `deploy`, `promote` and staging (SPEC-01b); contract generation (SPEC-03a); migrations and seeds (SPEC-04); the replacement object store (SPEC-05); Keycloak realm (SPEC-06); telemetry SDK wiring (SPEC-08). No product code.

## Design
- Paths and layering: ADR-001 and the AGENTS.md repo map. If a path must differ, update the map in this PR.
- Versions: lines in [TECH_STACK.md](../../../../docs/architecture/TECH_STACK.md); exact pins land in the lockfiles here. AG-UI SDK pins are SPEC-10's.
- `/healthz` returns `{"status":"ok","service":"<name>","version":"<git sha>"}`; `/readyz` checks only the dependencies that service has (PostgreSQL for api and worker, the object store for worker and render).
- No data changes. No contract changes.
- Expected diff: about 400 hand-written lines, mostly configuration; lockfiles excluded.

## Acceptance criteria
- AC1 (NFR-13): Given a fresh clone on a host with only Docker, make and git, when `make setup` then `make up` run, then every service in `compose.yaml` reports healthy and `/healthz` returns 200 on `api`, `worker`, `render` and `web`, with no manual step.
- AC2: Given the running stack, when `make check` runs, then lint, format check, type check and the tests of every layer run inside containers and exit 0; when any one fails, `make check` exits non-zero and names the failing step.
- AC3 (NFR-06): Given `.env.example`, when compared with the SECURITY.md inventory, then every key is present with a placeholder and no real value; `.env` is git-ignored; `make setup` never overwrites an existing `.env`.
- AC4 (ADR-015, NFR-12): Given `compose.yaml`, then every image is pinned by digest or built from a pinned base, `render` and `postgres` publish no host port, and published ports bind to `127.0.0.1` only.
- AC5: Given a target owned by a later spec (`contracts`, `release`, `deploy`, `promote`, `r0-sample`), when run, then it exits non-zero with a message naming that spec.
- AC6: Given `make down`, when run, then the stack stops and named volumes are kept; `make down CLEAN=1` removes them.

## Tests
- T-31 integration: `e2e/nfr/fresh-clone.sh` clones the branch into a temp directory, runs `make setup`, `make up`, waits for health, runs `make check`, then `make down CLEAN=1` (AC1, AC2, AC6). Runs nightly once SPEC-02 merges; run it locally for this PR.
- Unit: a trivial test per layer (`backend/tests/unit/test_health.py`, `agent/tests/`, `media/audio/tests/`, `media/scenes/tests/`, `web/tests/`, `contracts/tests/`) marked T-31 so every runner is exercised.
- Static: a script check that `.env.example` holds every SECURITY.md inventory key and no value matching a secret pattern (AC3); a Compose check that images carry digests and ports bind to 127.0.0.1 (AC4).

## Observability
Compose health checks on every service through `/healthz` and `/readyz`. No spans or metrics yet; SPEC-08 wires OpenTelemetry. Containers log JSON to stdout.

## Dependencies
None. Contracts: none. Size M (2 spec-days).
