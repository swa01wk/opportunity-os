Model: Composer 2.5 | Branch: feat/SPEC-05-object-store

Context: read plans/M0/specs/SPEC-05/spec.md,
docs/adr/ADR-015-local-object-store.md,
docs/adr/ADR-007-s3-object-storage.md,
docs/adr/ADR-009-provider-adapters.md,
docs/architecture/SECURITY.md,
docs/architecture/OBSERVABILITY.md (Retention and PII redaction),
.cursor/rules/backend.mdc (Storage),
backend/,
compose.yaml.
Task: implement SPEC-05 exactly as specified.
Boundaries: change only `backend/opportunityos/adapters/blob/`, `backend/tests/`, `infra/objectstore/`, `compose.yaml`, `.env.example` (storage keys only), `docs/adr/ADR-015-local-object-store.md`, the storage rows in `docs/architecture/TECH_STACK.md` and `docs/architecture/SECURITY.md`, and the risk line in `plans/STATUS.md`; do not change public contracts.
Tests: write the tests under "Tests" first, make them pass, run make check.
Rules: AGENTS.md and .cursor/rules apply; flag any new dependency; no secrets in code.
Report: changes made, tests added, any deviation from the spec and why.
