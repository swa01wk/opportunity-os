Model: Composer 2.5 | Branch: feat/SPEC-13-walking-skeleton

Context: read plans/M0/specs/SPEC-13/spec.md,
docs/design/screens/S-01-shell.html,
docs/design/tokens.md,
docs/product/UI_DESIGN.md (Studio frame, shared state rules),
docs/product/QUESTIONS.md (Q-43),
docs/contracts/openapi.yaml (diagnostic-runs),
docs/contracts/examples/agui/diagnostic-run.stream.jsonl,
docs/adr/ADR-020-ag-ui-event-stream.md,
docs/adr/ADR-022-delivery-pipeline-local-hosting.md,
docs/architecture/OBSERVABILITY.md,
backend/,
agent/,
media/scenes/,
web/.
Task: implement SPEC-13 exactly as specified.
Boundaries: change only the diagnostic route and workflow in `backend/`, the fixture upload in `infra/seed/`, `web/` (System check entry and panel, `web/lib/agui/`), `e2e/`, `infra/grafana/`, `.env.production.example`, `docs/ops/RUNBOOK.md`, the S-01 row note in `docs/product/UI_DESIGN.md` and the diagnostic row in `docs/architecture/OBSERVABILITY.md`; do not change public contracts.
Screens: match the screen's layout, copy and empty / loading / error states.
Rebuild it with the app's components and tokens; never copy its HTML.
Tests: write the tests under "Tests" first, make them pass, run make check.
Rules: AGENTS.md and .cursor/rules apply; flag any new dependency; no secrets in code.
Screen addition: the System check entry and panel are not in the S-01 prototype; build them only as A-43 describes, with the shell's components and tokens (approved as a screen change through Q-43, 14 Nov 2026).
Report: changes made, tests added, any deviation from the spec and why.
