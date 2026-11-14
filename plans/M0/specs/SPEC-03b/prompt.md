Model: Composer 2.5 | Branch: feat/SPEC-03b-contracts-events

Context: read plans/M0/specs/SPEC-03b/spec.md,
docs/contracts/events/domain-event.schema.json,
docs/contracts/agui/stream.json,
docs/contracts/analytics/events.schema.json,
docs/contracts/examples/agui/,
docs/adr/ADR-020-ag-ui-event-stream.md,
.cursor/rules/contracts.mdc,
contracts/.
Task: implement SPEC-03b exactly as specified.
Boundaries: change only `contracts/`, the three regenerated files, and `docs/contracts/examples/agui/diagnostic-run.stream.jsonl` (the change-log row is completed by SPEC-03e); change contracts only as this spec names (regenerate three files; add the diagnostic step names and example).
Tests: write the tests under "Tests" first, make them pass, run make check.
Rules: AGENTS.md and .cursor/rules apply; flag any new dependency; no secrets in code.
Report: changes made, tests added, any deviation from the spec and why.
