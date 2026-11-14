# SPEC-03c: Contracts III: agent task, execution and tool contracts in Pydantic
Milestone: M0 | Status: Draft (ready when SPEC-03a merges) | Layer: cross-cutting
Agent (if any): contracts only: `tasks.json`, TaskContract, ContextEnvelope, AgentResult; no task behaviour
Requirements: NFR-19, R-63 | Feature: F-17 (agent contracts) | ADRs: ADR-008, ADR-021
Screens: — | Branch: `feat/SPEC-03c-contracts-agent`

## Goal
The agent runtime codes against generated `TaskContract`, `ContextEnvelope`, `AgentResult`, task input and output and tool schemas, with `tasks.json` validated as data.

## Scope
In:
- Pydantic models for `agent-tools/task-io.schema.json`, `execution.schema.json` and `tools.schema.json`; a model for `tasks.json` entries, with `tasks.json` validated against it.
- Contract addition (A-43): task `diagnostic_echo` in `tasks.json` and its input and output in `task-io`: input is a short synthetic string; output echoes it with the model ID; `permittedTools: []`, one model call, small token budget, `maxRetries: 1`, `maxChildren: 0`, `outputDisposition` stored on the attempt only (no draft version), `reviewGate: none`; enabled only when `FEATURE_DIAGNOSTICS=1`.
- Register with the fixture harness.

Out: the runtime and tool host (SPEC-11a); research, script and storyboard behaviour (M2, M3).

## Design
Same rules and equivalence check as SPEC-03a. Expected diff: about 380 hand-written lines.

## Acceptance criteria
- AC1 (NFR-19): Given the three 0.4.0 schema files and `tasks.json`, when compared with the generated ones, then they are equivalent except for `diagnostic_echo`.
- AC2 (R-63): Given `tasks.json`, when validated, then every task has input and output schemas, permitted tools, budget, retry ceiling, failure states and `maxChildren: 0`.
- AC3: Given an `AgentResult` with a non-empty `proposedActions`, when validated, then both runtimes reject it (ADR-021).

## Tests
- T-33 contract: equivalence, `tasks.json` validation and the rejection case (AC1–AC3).

## Observability
None at runtime.

## Dependencies
SPEC-03a. Contracts: from 0.4.0. Size S (1 spec-day).
