Model: Composer 2.5 | Branch: feat/SPEC-11a-agent-runtime

Context: read plans/M0/specs/SPEC-11a/spec.md,
docs/adr/ADR-021-agent-runtime-contract.md,
docs/architecture/AGENT_ARCHITECTURE.md (Agent harness, Context and validation, Tools),
docs/contracts/agent-tools/,
.cursor/rules/agent.mdc,
agent/,
backend/opportunityos/workflows/.
Task: implement SPEC-11a exactly as specified.
Boundaries: change only `agent/` (runner, tools host, llm port and fake, prompts/diagnostic_echo.md, tests) and the agent step in `backend/opportunityos/workflows/`; do not change public contracts.
Tests: write the tests under "Tests" first, make them pass, run make check.
Rules: AGENTS.md and .cursor/rules apply; flag any new dependency; no secrets in code.
Report: changes made, tests added, any deviation from the spec and why.
