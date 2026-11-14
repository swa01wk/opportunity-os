Model: Composer 2.5 | Branch: feat/SPEC-12-render-skeleton

Context: read plans/M0/specs/SPEC-12/spec.md,
docs/contracts/media/render-job.schema.json,
docs/contracts/media/capabilities.json,
docs/contracts/examples/,
docs/adr/ADR-002-remotion-only-renderer.md,
docs/architecture/ARCHITECTURE.md (render service),
.cursor/rules/media.mdc,
media/scenes/.
Task: implement SPEC-12 exactly as specified.
Boundaries: change only `media/scenes/` (render service, tests, README), `docker/render/`, the render service block in `compose.yaml` and `infra/grafana/` (render panel); do not change public contracts.
Tests: write the tests under "Tests" first, make them pass, run make check.
Rules: AGENTS.md and .cursor/rules apply; flag any new dependency; no secrets in code.
Report: changes made, tests added, any deviation from the spec and why.
