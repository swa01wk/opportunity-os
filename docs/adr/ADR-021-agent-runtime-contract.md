# ADR-021: Agent runtime: task contract, context envelope and result acceptance
Status: Accepted (tech lead, 14 Nov 2026; owner to confirm at G2)    Date: 2026-11-14

## Context
PROCESS.md (Agent architecture) asks each agentic product to decide, before agent implementation, the harness interface and checkpoints (topic 2), task and event schemas (3), tool authorisation (4), leases and reconciliation (5) and context freshness and memory (6). OpportunityOS already has bounded task contracts (R-63, `tasks.json`), durable workflows (ADR-003) and version-bound approvals (R-41), but nothing bound an agent result to the exact inputs it read, so an owner's edit during a run could let a stale draft through (conformance C09). Requirements: R-50, R-51, R-52, R-63, NFR-01, NFR-05.

## Decision
- **Harness.** `agent.runner` implements a provider-neutral `AgentRuntime` (`start`, `resume`, `interrupt`, `cancel`, `inspect`, `subscribe`) as a thin loop over the `LlmProvider` adapter (ADR-009). No agent framework at R1–R2. DBOS steps are the checkpoints: a model-call step that did not complete restarts as a new attempt.
- **Contract per attempt.** Each attempt gets a `TaskContract` (static part from `tasks.json`; per-attempt run, attempt, idempotency key, input bindings, reservation) and a `ContextEnvelope` that lists every input version and hash it read. Both are stored on `task_attempt` (`input_bindings`). Schemas: `agent-tools/execution.schema.json`.
- **No memory, no delegation.** No state carries between runs; no task starts a child agent (`maxChildren: 0`).
- **Three validation stages,** in order, each with its own failure state: schema → policy and freshness (bindings still head, not cancelled, reservation held, tools allowlisted) → acceptance (postconditions, compiler). A result that passes is stored as a **draft version**; it is accepted only at its gate by a person.
- **Fencing.** Results are keyed by attempt; heads move only with `If-Match`; the storing transaction re-reads bound hashes and cancellation.
- **Tools.** The tool host checks `permittedTools` and budget before every call, and all agent tools stay read-only. There is no code-execution sandbox, because no generated code runs (NFR-05).
- **`AgentResult`** always has empty `proposedActions` and `proposedGraphChanges` at R1–R2.

## Alternatives
- **LangGraph or an agent SDK as the harness.** Adds its own state and checkpoint model next to DBOS (two competing state authorities) for three single-agent tasks. Revisit behind the same interface if R-64 chat or R-75 needs it, after the conformance tests pass.
- **Bind only the brief version.** Cheaper, but misses edits to claims, scripts and brand kits during a run.
- **Lock inputs while a task runs.** Blocks the owner from editing for minutes; rejecting stale results is simpler and honest.

## Consequences
- Easier: stale results are rejected by design (C09); each attempt is explainable from its stored bindings and validation stages; a framework can be added later behind the interface.
- Harder: every task must declare its input roles; a rejected stale result costs a re-run.
- Must do: contracts 0.3.0 (`execution.schema.json`, `tasks.json` fields, `task_attempt` columns); `.cursor/rules/agent.mdc` in Stage 3 states the runtime interface and stage order; C09 and C02 become `T-xx` in TEST_STRATEGY.md.
