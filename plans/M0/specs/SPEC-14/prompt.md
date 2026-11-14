Model: Composer 2.5 | Branch: feat/SPEC-14-search-provider

Context: read plans/M0/specs/SPEC-14/spec.md,
docs/product/QUESTIONS.md (Q-29),
docs/contracts/agent-tools/tools.schema.json (search_sources),
docs/adr/ADR-009-provider-adapters.md,
docs/adr/_template.md,
docs/sources/Strategy-v1.0.md (§5.1 topics only),
.cursor/rules/agent.mdc,
agent/,
backend/opportunityos/adapters/.
Task: implement SPEC-14 exactly as specified.
Boundaries: change only `backend/opportunityos/adapters/search/`, the tool registration in `agent/opportunityos_agent/tools/`, `agent/tests/`, `backend/tests/`, `docs/adr/ADR-023-search-provider.md`, `docs/adr/README.md`, the Q-29 row in `docs/product/QUESTIONS.md` and the search row in `docs/architecture/TECH_STACK.md`; do not change public contracts.
Tests: write the tests under "Tests" first, make them pass, run make check.
Rules: AGENTS.md and .cursor/rules apply; flag any new dependency; no secrets in code.
Report: changes made, tests added, any deviation from the spec and why.
