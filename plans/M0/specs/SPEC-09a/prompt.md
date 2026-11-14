Model: Composer 2.5 | Branch: feat/SPEC-09a-outbox

Context: read plans/M0/specs/SPEC-09a/spec.md,
docs/architecture/ARCHITECTURE.md (Write path),
docs/adr/ADR-010-outbox-events.md,
docs/adr/ADR-003-durable-execution-dbos.md,
docs/contracts/events/,
.cursor/rules/backend.mdc,
backend/.
Task: implement SPEC-09a exactly as specified.
Boundaries: change only `backend/opportunityos/domain/commands.py`, `backend/opportunityos/api/` (dependencies only), `backend/opportunityos/workflows/`, `backend/tests/` and `infra/grafana/` (outbox panel); do not change public contracts.
Tests: write the tests under "Tests" first, make them pass, run make check.
Rules: AGENTS.md and .cursor/rules apply; flag any new dependency; no secrets in code.
Report: changes made, tests added, any deviation from the spec and why.
