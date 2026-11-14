Model: Composer 2.5 | Branch: feat/SPEC-04-database

Context: read plans/M0/specs/SPEC-04/spec.md,
docs/contracts/db/schema.sql,
docs/adr/ADR-006-postgresql.md,
docs/adr/ADR-003-durable-execution-dbos.md,
docs/architecture/SECURITY.md (Authentication and roles, Secrets and credentials),
.cursor/rules/backend.mdc,
backend/.
Task: implement SPEC-04 exactly as specified.
Boundaries: change only `backend/migrations/`, `backend/opportunityos/repo/`, `backend/tests/`, `infra/seed/` and the `migrate` / `seed` Make targets; do not change public contracts.
Tests: write the tests under "Tests" first, make them pass, run make check.
Rules: AGENTS.md and .cursor/rules apply; flag any new dependency; no secrets in code.
Report: changes made, tests added, any deviation from the spec and why.
