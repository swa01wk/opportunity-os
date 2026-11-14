Model: Composer 2.5 | Branch: feat/SPEC-11b-openai-adapter

Context: read plans/M0/specs/SPEC-11b/spec.md,
docs/adr/ADR-014-llm-provider.md,
docs/adr/ADR-009-provider-adapters.md,
docs/architecture/SECURITY.md (Provider data-use terms),
.cursor/rules/agent.mdc (Prompts and models, Eval scenarios),
agent/.
Task: implement SPEC-11b exactly as specified.
Boundaries: change only `agent/opportunityos_agent/llm/`, `agent/evals/`, `agent/tests/`, the `eval` Make target and the agent manifest and lockfile; do not change public contracts.
Tests: write the tests under "Tests" first, make them pass, run make check.
Rules: AGENTS.md and .cursor/rules apply; flag any new dependency; no secrets in code.
Report: changes made, tests added, any deviation from the spec and why.
