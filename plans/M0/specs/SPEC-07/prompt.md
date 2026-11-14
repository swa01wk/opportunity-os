Model: Composer 2.5 | Branch: feat/SPEC-07-studio-shell

Context: read plans/M0/specs/SPEC-07/spec.md,
docs/design/screens/S-01-shell.html,
docs/design/screens/S-02-projects.html (frame only),
docs/design/tokens.md,
docs/product/UI_DESIGN.md (Studio frame, S-01 row, states),
docs/contracts/openapi.yaml (/me),
docs/adr/ADR-005-nextjs-studio.md,
docs/adr/ADR-012-auth-provider.md,
docs/adr/ADR-018-studio-ui-kit.md,
web/.
Task: implement SPEC-07 exactly as specified.
Boundaries: change only `web/`, `e2e/screens/` and `e2e/smoke/`; do not change public contracts.
Screens: match the screen's layout, copy and empty / loading / error states.
Rebuild it with the app's components and tokens; never copy its HTML.
Tests: write the tests under "Tests" first, make them pass, run make check.
Rules: AGENTS.md and .cursor/rules apply; flag any new dependency; no secrets in code.
Report: changes made, tests added, any deviation from the spec and why.
