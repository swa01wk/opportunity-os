Model: Composer 2.5 | Branch: feat/SPEC-06-api-auth

Context: read plans/M0/specs/SPEC-06/spec.md,
docs/contracts/openapi.yaml (/me, problem responses),
docs/adr/ADR-012-auth-provider.md,
docs/adr/ADR-004-fastapi-api.md,
docs/architecture/SECURITY.md (Authentication and roles, threat model TH-01, TH-02),
.cursor/rules/backend.mdc,
backend/,
infra/.
Task: implement SPEC-06 exactly as specified.
Boundaries: change only `backend/opportunityos/api/`, `backend/opportunityos/domain/authz.py`, `backend/opportunityos/adapters/identity/`, `backend/tests/`, `infra/keycloak/`, `infra/seed/` and `.env.example` (the two dev owner keys); do not change public contracts.
Tests: write the tests under "Tests" first, make them pass, run make check.
Rules: AGENTS.md and .cursor/rules apply; flag any new dependency; no secrets in code.
Report: changes made, tests added, any deviation from the spec and why.
