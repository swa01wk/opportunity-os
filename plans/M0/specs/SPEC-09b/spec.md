# SPEC-09b: DBOS kill-and-resume spike: idempotent steps, retry ceilings and the fault suite (ADR-003)
Milestone: M0 | Status: Draft (ready when SPEC-09a merges) | Layer: backend
Agent (if any): —
Requirements: NFR-01, R-50, R-51 | Feature: F-14 | ADRs: ADR-003
Screens: — | Branch: `feat/SPEC-09b-dbos-spike`

## Goal
We know, by test, that DBOS resumes a workflow after the worker is killed mid-step without repeating a paid call, and ADR-003 records the result before M1 depends on it.

## Scope
In:
- Step helper `workflows/steps.py`: each step keyed by attempt ID or input hash, result stored by that key, `task_attempt` projection written per attempt (status, error class, retries), retry ceiling from configuration, unknown external outcome recorded as `uncertain_external`, never assumed successful.
- Spike workflow under `APP_ENV=test`: three steps that call a fake provider which counts calls by idempotency key and can be told to hang or fail.
- Fault suite (T-90 short set): kill the worker container during a provider call and during the step's result write; duplicate relay delivery; provider timeout; provider "accepted but no answer". After restart, check call counts, step results and projections.
- Workflow version pinning check (C12, spike part): a run started on workflow version 1 resumes on version 1 after a deploy that registers version 2, or is listed for documented migration.
- Result recorded in ADR-003 (amendment line: pass, with the DBOS version) or, on failure, an ADR superseding ADR-003 proposed in this PR and flagged to you before M1.

Out: budget reservation (SPEC-29); cancel, resume and takeover commands (SPEC-40, SPEC-66).

## Design
Rules: backend.mdc (Workflows). The spike code stays as the reusable step helper and test fixtures. Expected diff: about 380 lines, most of it tests.

## Acceptance criteria
- AC1 (C04, NFR-01): Given the worker is killed after a fake provider accepted a call, when the worker restarts, then the workflow resumes and the provider count for that idempotency key stays 1.
- AC2 (R-51 AC1): Given a step that keeps failing, when it retries, then it stops at the configured ceiling, each retry is a new `task_attempt`, and the run ends `failed` with the error class.
- AC3 (NFR-01): Given a provider that accepted the request and never answered, when the step times out, then the attempt is recorded `uncertain_external` and no automatic retry repeats the call.
- AC4 (C12): Given a run started on workflow version 1, when version 2 is deployed, then the run completes on version 1's steps.
- AC5: Given the suite's results, then ADR-003 has its amendment line (or a superseding ADR is proposed and STATUS.md flags it).

## Tests
- T-04 fault (C04): kill after an external write, no duplicate effect (AC1). Short form every PR, full form nightly.
- T-90 fault: worker kill mid-call, duplicate relay, provider timeout, unknown outcome (AC1–AC3).
- T-12 fault (C12, spike part): pinned workflow version honoured (AC4). Completed by SPEC-83.

## Observability
Workflow and step spans; metrics `oos.run.duration_seconds`, `oos.run.active`, `oos.step.retries{step}`; log events `run.state_changed`, `run.recovered_after_restart` (OBSERVABILITY.md).

## Dependencies
SPEC-09a. Contracts: generated set. Size M (2 spec-days). Risk owner: this spec closes the DELIVERY_PLAN.md RAID risk on DBOS.
