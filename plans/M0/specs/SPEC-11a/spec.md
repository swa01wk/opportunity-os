# SPEC-11a: Agent runtime, tool host, validation stages and fake model (ADR-021)
Milestone: M0 | Status: Draft (ready when SPEC-03c and SPEC-09b merge) | Layer: agent
Agent (if any): runtime for every task; task contract `diagnostic_echo` (A-43); maturity: not applicable (harness); eval scenarios: none (runner in SPEC-11b); conformance C02, C08 guard, C09 harness part
Requirements: R-63, NFR-05, NFR-11 | Feature: F-17 | ADRs: ADR-021, ADR-009, ADR-003
Screens: — | Branch: `feat/SPEC-11a-agent-runtime`

## Goal
A worker step can run any task from `tasks.json` through one bounded `AgentRuntime` that builds the task contract and context envelope, allows only permitted read-only tools within budget, and stores a result only after schema, freshness and acceptance checks pass.

## Scope
In:
- `agent/opportunityos_agent/runner/`: `AgentRuntime` (`start`, `resume`, `interrupt`, `cancel`, `inspect`, `subscribe`) as a thin loop over the `LlmProvider` port, per [agent.mdc](../../../../.cursor/rules/agent.mdc#runtime-adr-021) and [ADR-021](../../../../docs/adr/ADR-021-agent-runtime-contract.md).
- `TaskContract` built from `tasks.json` plus per-attempt fields; `ContextEnvelope` with every input version and hash read; both stored on `task_attempt` (`input_bindings`, `validation`).
- Tool host in `agent/opportunityos_agent/tools/host.py` in the agent.mdc order: permitted check → budget check → adapter call → summary. No tools are registered yet except test fixtures.
- Validation stages: schema → policy and freshness (through a `HeadReader` port that re-reads bound heads; fake in tests) → acceptance (postcondition hook per task). Failure states from `tasks.json`; mapping to R-53 error classes.
- `LlmProvider` port in `agent/opportunityos_agent/llm/` with a deterministic `FakeLlmProvider` (scripted responses from fixture files, can ask for any tool) and `estimate_cost`.
- `diagnostic_echo` task (prompt `agent/prompts/diagnostic_echo.md`, prompt SHA-256 recorded) and the worker step that runs a task from a DBOS step using the SPEC-09b step helper.
- `maxChildren: 0` guard: any child-agent request is refused.

Out: the OpenAI adapter and the eval runner (SPEC-11b); search and fetch tools (SPEC-14, SPEC-32); research, script, storyboard tasks (M2, M3).

## Design
Golden rules, tool host order, validation stages and untrusted-content rules are owned by agent.mdc and AGENT_ARCHITECTURE.md. `proposedActions` and `proposedGraphChanges` are always empty. Expected diff: about 420 lines including tests.

## Acceptance criteria
- AC1 (C02, R-63): Given a fake model that requests a tool outside `permittedTools`, when the tool host handles it, then the call is denied before any adapter is touched, the decision is logged as `agent.tool_denied` with a coded reason, and the attempt continues or fails per the task's failure states.
- AC2 (R-63): Given a task at its model-call, tool-call or token ceiling, when the model asks for more, then the runtime stops the attempt with `budget_exhausted` and no further call is made.
- AC3 (C09 harness part): Given a bound input whose head changes while the fake model is running, when the result reaches the freshness stage, then it is rejected as `stale_input`, logged `agent.stale_result_rejected`, and nothing is stored.
- AC4 (NFR-05): Given model output that fails the output schema, then it is rejected as `schema_invalid`; no part of any model output is executed, imported or rendered as code.
- AC5 (C08 guard): Given a contract or model request for a child agent, then it is refused and `maxChildren` stays 0.
- AC6: Given `diagnostic_echo` with the fake model, when run from a DBOS step, then `task_attempt` records the prompt SHA-256, model ID, input bindings and all three validation stages as passed.

## Tests
- T-02 agent mocked (C02): denied tool before effect (AC1).
- T-08 contract (C08): `maxChildren` guard (AC5).
- T-09 agent mocked (C09, harness part): stale input rejected (AC3). Extended by SPEC-33, SPEC-43, SPEC-47, SPEC-62.
- Agent mocked in `agent/tests/`: budget ceilings, schema rejection, attempt record (AC2, AC4, AC6).

## Observability
Spans `agent.<task>.run` → `call_model`, `tool.<name>`; metrics `oos.agent.tool_calls`, `oos.agent.failure{state}`, `oos.agent.validation{stage,outcome}`, `oos.agent.tool_denied`, `oos.agent.budget_used_ratio`, GenAI token attributes; log events `agent.output_rejected`, `agent.stale_result_rejected`, `agent.tool_denied` (OBSERVABILITY.md). No prompt or output bodies in telemetry.

## Dependencies
SPEC-03c (generated agent contracts, `diagnostic_echo`), SPEC-09b (step helper; DBOS confirmed). Contracts: 1.0.0 agent-tools. Size M (2 spec-days).
