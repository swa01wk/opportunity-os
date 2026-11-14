Model: Composer 2.5 | Branch: feat/SPEC-03c-contracts-agent

Context: read plans/M0/specs/SPEC-03c/spec.md,
docs/contracts/agent-tools/,
docs/adr/ADR-021-agent-runtime-contract.md,
docs/architecture/AGENT_ARCHITECTURE.md (Execution contract),
.cursor/rules/contracts.mdc,
contracts/.
Task: implement SPEC-03c exactly as specified.
Boundaries: change only `contracts/`, the regenerated `docs/contracts/agent-tools/` files, and `tasks.json` (the change-log row is completed by SPEC-03e); change contracts only as this spec names (regenerate agent-tools; add `diagnostic_echo`).
Tests: write the tests under "Tests" first, make them pass, run make check.
Rules: AGENTS.md and .cursor/rules apply; flag any new dependency; no secrets in code.
Report: changes made, tests added, any deviation from the spec and why.
