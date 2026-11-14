Model: Composer 2.5 | Branch: feat/SPEC-03a-contracts-pipeline

Context: read plans/M0/specs/SPEC-03a/spec.md,
docs/adr/ADR-008-pydantic-canonical-schema.md,
docs/contracts/README.md,
docs/contracts/common.schema.json,
docs/contracts/events/workflow-request.schema.json,
docs/contracts/examples/,
docs/product/QUESTIONS.md (Q-43),
.cursor/rules/contracts.mdc,
contracts/.
Task: implement SPEC-03a exactly as specified.
Boundaries: change only `contracts/`, the two regenerated schema files, `docs/contracts/README.md` (change-log row) and the `contracts` / `contracts-check` Make targets; change contracts only as this spec names (regenerate two files; add `diagnostic`).
Tests: write the tests under "Tests" first, make them pass, run make check.
Rules: AGENTS.md and .cursor/rules apply; flag any new dependency; no secrets in code.
Report: changes made, tests added, any deviation from the spec and why.
