# SPEC-11b: OpenAI LlmProvider adapter, portability fixtures and the eval runner
Milestone: M0 | Status: Draft (ready when SPEC-11a merges) | Layer: agent
Agent (if any): adapter for every task; eval scenarios: `diagnostic_echo` suite (runner proof); maturity: not applicable; conformance: none
Requirements: NFR-11, R-63 | Feature: F-17 | ADRs: ADR-014, ADR-009
Screens: — | Branch: `feat/SPEC-11b-openai-adapter`

## Goal
Agent tasks can run on the pinned OpenAI model through the same `LlmProvider` port as the fake, proven by shared fixtures, and `make eval` runs eval suites with the fake by default and the real model with `LIVE=1`.

## Scope
In:
- `OpenAiLlmProvider` in `agent/opportunityos_agent/llm/openai.py` (OpenAI Python SDK): model from configuration (`gpt-5.4-mini-2026-03-17`, ADR-014), structured output against the task's output schema, tool calling, `store: false`, timeouts, attempt ID as idempotency metadata, token usage and `estimate_cost`; provider errors mapped to `retryable_provider` or `invalid_content`.
- Shared adapter fixtures in `agent/tests/adapters/`: the same cases run against the fake and, when `LIVE=1`, the OpenAI adapter (structured output parses, tool call shape, refusal mapping, timeout mapping).
- Eval runner skeleton in `agent/evals/` per the scenario format in agent.mdc: discovers suites, runs with the fake by default, real with `LIVE=1`, records per run the prompt SHA-256, model, tokens, cost and outcome; one `diagnostic_echo` suite with two scenarios to prove the runner. `make eval` calls it.
- `OPENAI_API_KEY` stays in `.env` only; live runs record spend (Q-05).

Out: task suites and thresholds (SPEC-33, SPEC-43, SPEC-47); TTS adapter (SPEC-21).

## Design
SDK calls appear only in `agent/opportunityos_agent/llm/` (backend.mdc layering). No fallback model at R1 (agent.mdc). Expected diff: about 350 lines.

## Acceptance criteria
- AC1 (NFR-11): Given the shared adapter fixtures, when run against the fake and against the OpenAI adapter with `LIVE=1`, then both pass the same cases with no change to contracts.
- AC2: Given any OpenAI request, then it sets `store: false` and contains no secret, personal data or signed URL (checked by a request-capture test).
- AC3: Given a provider timeout or 5xx, then the adapter raises `retryable_provider`; given a schema-violating response, then the runtime's schema stage rejects it.
- AC4: Given `make eval`, then the `diagnostic_echo` suite runs with the fake and writes a run record; with `LIVE=1` it calls the real model and records tokens and cost.

## Tests
- T-91 functional (portability, LLM part): shared fixtures pass for both adapters (AC1, AC3). Fake every PR; live weekly.
- Agent mocked: request capture for `store: false` and content rules (AC2); eval runner run record (AC4).

## Observability
GenAI span attributes (`gen_ai.request.model`, token usage) on `call_model`; metric `oos.cost.actual_minor{provider=openai}` when live; log event `llm.provider_error` (class only).

## Dependencies
SPEC-11a. Contracts: 1.0.0. Size M (2 spec-days). Your dependency: an OpenAI key for development in `.env` (DELIVERY_PLAN.md dependencies).
