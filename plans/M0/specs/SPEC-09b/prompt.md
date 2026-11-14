Model: Composer 2.5 | Branch: feat/SPEC-09b-dbos-spike

Context: read plans/M0/specs/SPEC-09b/spec.md,
docs/adr/ADR-003-durable-execution-dbos.md,
docs/architecture/ARCHITECTURE.md (Write path),
plans/TEST_STRATEGY.md (Conformance scenarios),
.cursor/rules/backend.mdc (Workflows),
backend/opportunityos/workflows/.
Task: implement SPEC-09b exactly as specified.
Boundaries: change only `backend/opportunityos/workflows/`, `backend/opportunityos/adapters/` (test fake provider only), `backend/tests/conformance/`, `backend/tests/functional/`, `docs/adr/ADR-003-durable-execution-dbos.md` and, only on failure, a new ADR file; do not change public contracts.
Tests: write the tests under "Tests" first, make them pass, run make check.
Rules: AGENTS.md and .cursor/rules apply; flag any new dependency; no secrets in code.
Report: changes made, tests added, any deviation from the spec and why.
