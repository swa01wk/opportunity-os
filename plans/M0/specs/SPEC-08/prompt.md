Model: Composer 2.5 | Branch: feat/SPEC-08-telemetry

Context: read plans/M0/specs/SPEC-08/spec.md,
docs/architecture/OBSERVABILITY.md,
docs/adr/ADR-016-observability-stack.md,
.cursor/rules/observability.mdc,
backend/,
media/scenes/,
web/,
compose.yaml.
Task: implement SPEC-08 exactly as specified.
Boundaries: change only telemetry setup modules in `backend/`, `agent/`, `media/scenes/`, `media/audio/` and `web/`, `infra/otel/`, `infra/grafana/` and `compose.yaml`; do not change public contracts.
Tests: write the tests under "Tests" first, make them pass, run make check.
Rules: AGENTS.md and .cursor/rules apply; flag any new dependency; no secrets in code.
Report: changes made, tests added, any deviation from the spec and why.
