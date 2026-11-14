Model: Composer 2.5 | Branch: feat/SPEC-10-agui-relay

Context: read plans/M0/specs/SPEC-10/spec.md,
docs/adr/ADR-020-ag-ui-event-stream.md,
docs/contracts/agui/stream.json,
docs/contracts/examples/agui/,
docs/architecture/AGENT_ARCHITECTURE.md (AG-UI in OpportunityOS),
docs/architecture/SECURITY.md (TH-31, TH-32),
.cursor/rules/backend.mdc,
.cursor/rules/observability.mdc,
backend/.
Task: implement SPEC-10 exactly as specified.
Boundaries: change only `backend/opportunityos/workflows/agui.py`, the relay sink in `backend/opportunityos/workflows/`, the events route in `backend/opportunityos/api/`, `backend/tests/`, `contracts/tests/` (stream validation), the two SDK pins in `backend` and `web` manifests and lockfiles, and `infra/grafana/` (stream panel); do not change public contracts.
Tests: write the tests under "Tests" first, make them pass, run make check.
Rules: AGENTS.md and .cursor/rules apply; flag any new dependency; no secrets in code.
Report: changes made, tests added, any deviation from the spec and why.
