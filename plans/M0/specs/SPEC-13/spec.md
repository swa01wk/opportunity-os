# SPEC-13: Walking skeleton: web → api → worker → agent → render, traced and deployed to staging
Milestone: M0 | Status: Draft (ready when SPEC-01b, SPEC-07, SPEC-08, SPEC-10, SPEC-11a and SPEC-12 merge) | Layer: cross-cutting (backend, frontend, agent, media)
Agent (if any): `diagnostic_echo` (fake model by default); conformance C01 (HTTP), C03
Requirements: NFR-09, NFR-13 | Feature: — (cross-cutting; M0 exit) | ADRs: ADR-003, ADR-020, ADR-021, ADR-022
Screens: S-01 (docs/design/screens/S-01-shell.html), with the System check element of A-43 | Branch: `feat/SPEC-13-walking-skeleton`

## Goal
Signed in to an empty Studio, you press Run system check and watch one run go web → api → worker → agent (fake) and render → back to the Studio as live steps, with one trace across every service, on a release deployed to local staging.

## Scope
In:
- API: `POST /v1/projects/{projectId}/diagnostic-runs` per `openapi.yaml` 1.0.0: owner or editor, `Idempotency-Key`, write path from SPEC-09a, 202 with the run; 404 when `FEATURE_DIAGNOSTICS` is off.
- Worker: `diagnostic` workflow: two steps in parallel, `diagnostic.echo` (SPEC-11a runtime, `diagnostic_echo`, fake model unless configured) and `diagnostic.validate` (SPEC-12 `validate` job on the odd-squares VideoSpec, uploaded to the object store by `make seed`), then `diagnostic.join` exactly once when both finish; projections and outbox events on each step.
- Web (A-43): in the app shell, next to the environment badge, a **System check** entry shown only when `FEATURE_DIAGNOSTICS` is on. It opens a panel with "Run system check", then the three steps with their state from the project's AG-UI stream (SPEC-10), the outcome, run ID and trace ID. A minimal stream client in `web/lib/agui/` (snapshot, cursor, drop duplicates, reconnect) that SPEC-34 extends rather than replaces. Live region for step changes; status as text and icon.
- Staging: tag `v0.1.0-rc.1`, `make release`, `make deploy ENV=staging` with `FEATURE_DIAGNOSTICS=1`, then T-41 against staging. `FEATURE_DIAGNOSTICS=0` in `.env.production.example`.
- Docs: a RUNBOOK.md entry "Run the system check"; UI_DESIGN.md S-01 row note for the System check (dev and staging only), approved through Q-43 on 14 Nov 2026.

Out: the full run indicator, error panel and S-13 (SPEC-34, SPEC-40); budget reservation (the diagnostic task's spend is recorded, not reserved; SPEC-29).

## Design
- Uses only contracts from 1.0.0; no contract change here.
- The diagnostic run attaches to the seeded synthetic project; the panel uses the first project the member can see.
- Expected diff: about 400 lines across four layers; each layer's part is small because the plumbing exists.

## Acceptance criteria
- AC1 (M0 exit, NFR-09): Given the signed-in owner on staging, when they press Run system check, then the panel shows `diagnostic.echo`, `diagnostic.validate` and `diagnostic.join` reaching done, and the outcome "Passed" with run ID and trace ID.
- AC2 (NFR-09): Given that run's trace ID, when queried in Tempo, then the trace holds spans from `web`, `api`, `worker`, the agent task and `render`, with `oos.run_id` and `oos.task_attempt_id` on the worker, agent and render spans.
- AC3 (C03): Given both parallel steps finishing at the same moment, when the workflow continues, then `diagnostic.join` runs once and one `run.state_changed` to succeeded is written.
- AC4 (C01): Given two POSTs with the same `Idempotency-Key`, then one run exists and both get the same 202 body.
- AC5 (NFR-13): Given release `v0.1.0-rc.1`, when deployed with `make deploy ENV=staging`, then staging runs the recorded digests and AC1 passes there.
- AC6: Given `FEATURE_DIAGNOSTICS=0`, then the System check entry is absent and the endpoint returns 404.
- AC7 (R-61): Given the stream drops during a run, then the panel shows "Live updates paused, reconnecting" and, after reconnect, the correct step states with no duplicate rows.

## Tests
- T-41 Playwright (smoke every PR, and on staging for M0 exit): sign in, run the system check, all steps done (AC1, AC6, AC7).
- T-38 integration (extension): the trace spans every service (AC2).
- T-03 functional (C03): simultaneous completion of the two steps, join once (AC3).
- T-01 functional (C01, HTTP part): duplicate POST (AC4).
- T-15 Playwright (extension): the System check entry and panel states in the shell.
- T-98 (from SPEC-01b) run for `v0.1.0-rc.1` (AC5).

## Observability
Spans for the new route, workflow and steps with correlation attributes; `run.state_changed` log events; a "Walking skeleton" panel (runs by outcome, step duration) on the Stack health dashboard; OBSERVABILITY.md gets the `diagnostic` workflow in its signals table.

## Dependencies
SPEC-01b, SPEC-07, SPEC-08, SPEC-10, SPEC-11a, SPEC-12 (and through them SPEC-03e, SPEC-06, SPEC-09a, SPEC-09b). A-43 accepted 14 Nov 2026. Contracts: 1.0.0. Size M (2 spec-days).
