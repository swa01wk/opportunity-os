# Agent architecture

Status: **Draft for G2** (Stage 2c addendum, 13 Nov 2026). Follows the "Agent architecture" section of [PROCESS.md](../PROCESS.md#agent-architecture). Baselined at G2; after that it changes only through change control.

Owners of related facts: containers and components [ARCHITECTURE.md](ARCHITECTURE.md) · task contracts [tasks.json](../contracts/agent-tools/tasks.json) and [task-io.schema.json](../contracts/agent-tools/task-io.schema.json) · tools [tools.schema.json](../contracts/agent-tools/tools.schema.json) · AG-UI stream [contracts/agui/](../contracts/agui/stream.json) · threats [SECURITY.md](SECURITY.md#agent-risks-prompt-injection-excessive-agency-generated-code) · telemetry [OBSERVABILITY.md](OBSERVABILITY.md) · decisions ADR-003 (durable workflows), ADR-009 (adapters), ADR-014 (model), [ADR-020](../adr/ADR-020-ag-ui-event-stream.md) (AG-UI).

## Shape

OpportunityOS's agents are not conversational at R1–R2. A person starts work with a structured command in the Studio. A durable workflow runs a bounded agent task. The result is a new **draft version** that a person reviews at a gate. There is no chat (A-28; R-64 is Could). So in this product:

- the "turn" is a **task run** inside a workflow, not a chat message;
- **routing is the workflow**, fixed in code; no model decides which agent runs;
- the Studio follows runs through **AG-UI events** on the project's event stream (ADR-020).

## Design rules, applied

| Rule (PROCESS.md) | How OpportunityOS meets it | Where |
|---|---|---|
| 1 One runtime, many agents | The three tasks (research, script, storyboard) share `agent.runner` in the worker. A task is one entry in `tasks.json`, a prompt and an output schema, not a service | ADR-001, ADR-003 |
| 2 Stateless per turn | Each task attempt is a DBOS step; versions, attempts and costs live in PostgreSQL. A restart resumes from the last completed step | ADR-003 |
| 3 The model understands; code decides | Models return typed data (claims, beats, VideoSpec). Schema checks, the compiler, demonstration functions, budgets, approvals and publication are code. Nothing a model writes is executed | NFR-05, TH-15 |
| 4 Route deterministically first | There is no model routing. Command → workflow type → task is fixed: `workflow-request.schema.json` `type` enum and `wf.production` | R-63 |
| 5 The router runs rarely | Does not apply: there is no router at R1–R2 | — |
| 6 People approve consequential actions | Gates A–E are REST commands bound to a version hash (R-40, R-41). Agents and services have no route to approval or publication (R-43, TH-04). Agent output is always a draft | SECURITY.md |
| 7 Bounded and untrusted | `tasks.json`: input/output schema, permitted tools, token and call budgets, retry ceiling, timeout, failure states, postconditions. Fetched pages are data; `injection_detected` is a failure state | TH-12–TH-14 |
| 8 Observable by default | Span per task, model call and tool call, with `gen_ai` attributes, cost and prompt hash | OBSERVABILITY.md |

## One run, in one picture

```
Studio (S-03 … S-11): a button such as "Start research" or "Render draft preview"
   │  REST command: bearer token, Idempotency-Key, If-Match  →  202 Run
   ▼
api: authenticate → responsibility check → project state allows it → preflight and budget
   → ONE transaction: domain change + workflow_request + outbox event + audit row
   ▼
worker: dispatcher → DBOS workflow (workflow ID = request ID, so a duplicate start is a no-op)
   step: reserve the estimated cost (row lock)
   step: agent.runner(task)
           model call ↔ read-only tools (search_sources, fetch_source, compute_demonstration,
                                          list_capabilities, validate_scene_spec)
           → output schema check → postconditions → retry up to the ceiling
           → new DRAFT version (claims, script or storyboard), never an approval
   step: code-only services (demonstration, TTS and alignment, compile and render, media QA)
   step: settle actual cost → outbox events
   ▼
relay: outbox → AG-UI events → GET /projects/{projectId}/events (SSE)
   → Studio: run indicator, S-13 attempt timeline, query refresh
   ▼
A person reviews the draft and approves the gate (REST, version-bound)
```

## Routing sources of truth

| What | Where | Rule |
|---|---|---|
| Command → workflow type | `openapi.yaml` operations; `workflow-request.schema.json` `type` enum | Closed enum; a model never chooses the workflow |
| Workflow → steps and tasks | `wf.production` (code); [production workflow](ARCHITECTURE.md#production-workflow) | Deterministic |
| Task contract | `tasks.json`, `task-io.schema.json` | One entry per task: tools, budgets, retries, timeout, failure states, postconditions |
| Tool allowlist | `tools.schema.json`, `permittedTools` per task | Read-only tools only |
| Responsibility → command | [SECURITY.md responsibility matrix](SECURITY.md#authentication-and-roles) | Checked in the API before any workflow request |
| Project state → allowed commands | Production state machine (ARCHITECTURE.md) | For example, a storyboard run needs Gate B approved |
| Animation operations a storyboard may use | `media/capabilities.json` | The compiler rejects anything else (`CAPABILITY_UNSUPPORTED`) |
| Run → AG-UI events | [contracts/agui/stream.json](../contracts/agui/stream.json) | Mapping fixed in the relay |

## Agent catalogue

| Agent task | Owns | What it does for the operator | Tools and systems | Who approves, at which gate | R-xx, US-xx |
|---|---|---|---|---|---|
| research | Claim and evidence drafts | Finds sources, extracts claims with short excerpts, lists unsupported gaps | `search_sources`, `fetch_source`, `compute_demonstration`; SearchProvider (Q-29), SourceFetcher | Reviewer marks each claim on S-05; Gate B on S-06 | R-08, R-09; US-03 |
| script | Script versions | Writes narration beats in the series structure, each with claim references | none | Gate B on S-06 | R-14, R-57; US-05 |
| storyboard | Storyboard versions (VideoSpec) | Plans scenes, objects and actions from the capability catalogue and checks them with the compiler | `list_capabilities`, `compute_demonstration`, `validate_scene_spec` | Gate C on S-07 | R-16, R-18–R-22; US-06 |

**Code-only paths (no model):** demonstrations from allowlisted functions (R-11–R-13); narration TTS, alignment and captions (R-25–R-27); compiler, render and media QA (R-28–R-30); revision impact (R-31, R-32); cost reservation (R-34).

**No agent yet:** chat drafting (R-64, Could, A-28); model critique in QA (R-65, Could); R3 diagnostic recommendations (R-75, after A-18). Each would be added with the steps below.

## Adding an agent task

Each new task is a spec (`SPEC-xx`) and needs an `R-xx` that asks for it.

1. Add the task to `tasks.json` and its input and output to `task-io.schema.json` (contract minor version).
2. Reuse or add tools in `tools.schema.json`; tools stay read-only; list them in `permittedTools`.
3. Write the prompt in `agent/prompts/<task>.md`, versioned; each attempt records the prompt hash.
4. Add the command and workflow type that starts it (`openapi.yaml`, `workflow-request.schema.json`) and its step in `wf.production`, with budget reservation and the retry ceiling.
5. Check postconditions in code and map every failure state to an error class (R-53).
6. Store the output as a new draft version and name the gate that reviews it.
7. Add its step names, tool-call summaries and activity types to `contracts/agui/stream.json`, and its Studio surface on the design canvas.
8. Add tests: eval fixtures in `agent/evals/<task>/` (valid, invalid, injection), mocked unit tests, and a recorded AG-UI stream replayed in Playwright.
9. Add telemetry (spans, `oos.agent.*` metrics), its row in the catalogue above, and its row in `STATUS.md`.

## Supporting layers

| Layer | What | Decision |
|---|---|---|
| Model provider | `LlmProvider` adapter; structured outputs | ADR-014, ADR-009 |
| Search and fetch | `SearchProvider` (Q-29), `SourceFetcher` with the SSRF guard | ADR-009, TH-12 |
| Narration | `TtsProvider` with timestamps | ADR-013 |
| Durable execution and state | DBOS Transact on PostgreSQL | ADR-003, ADR-006 |
| Artifacts | Content-addressed object store | ADR-007 |
| Telemetry | OpenTelemetry, Grafana LGTM | ADR-016 |
| Agent ↔ UI | AG-UI events on the project stream | ADR-020 |

There is no retrieval index or vector store (SECURITY.md, LLM08 does not apply). There is no MCP or A2A at R1–R2: tools are in-process functions behind the tool host, and there is only one agent runtime. MCP is reconsidered only if tools must be shared with other agents.

## AG-UI in OpportunityOS

Decision: [ADR-020](../adr/ADR-020-ag-ui-event-stream.md). Contract: [contracts/agui/stream.json](../contracts/agui/stream.json). Example: [examples/agui/preview-run.stream.jsonl](../contracts/examples/agui/preview-run.stream.jsonl).

**How we use it.** One SSE stream per open project, `GET /projects/{projectId}/events`, carries AG-UI events encoded with the AG-UI SDK. The thread ID is the project ID, and the run ID is the execution run ID. Runs are started by REST commands, not by an AG-UI run request: production runs are durable and outlive the browser connection, so the Studio observes them rather than holding them open. The AG-UI run request is used only if chat drafting (R-64) is promoted.

| Source | AG-UI event | What the Studio does |
|---|---|---|
| Run starts (`run.state_changed` → running) | `RUN_STARTED` | Run indicator appears |
| Run succeeds | `RUN_FINISHED` | Indicator clears; affected queries refresh |
| Run fails or is cancelled | `RUN_ERROR` with `code` = error class (`retryable_provider`, `invalid_content`, `render_defect`, `uncertain_external`, `resource_limit`, …) | Error panel with the matching repair (R-53) |
| Workflow step or task attempt starts and finishes | `STEP_STARTED`, `STEP_FINISHED` (step names in the contract, e.g. `research`, `tts.scene.explain`, `render.clip.scene.payoff`, `assembly`, `qa`) | "Step 3 of 4" in the run indicator and S-13 |
| Agent tool call | `TOOL_CALL_START`, `TOOL_CALL_ARGS`, `TOOL_CALL_END`, `TOOL_CALL_RESULT`, as summaries | S-13 attempt timeline, e.g. "fetched 5 sources, 1 refused" |
| Long work progress and pauses | `ACTIVITY_SNAPSHOT`, `ACTIVITY_DELTA` (`opportunityos.render_progress`, `opportunityos.run_paused`) | Per-scene render progress; "paused for budget" or "waiting for approval" |
| Connect or reconnect | `STATE_SNAPSHOT`: active runs and their current step | Recovers without replaying anything |
| Every domain event | `CUSTOM`, name `opportunityos.<event type>`, value = the DomainEvent | TanStack Query invalidation (ADR-018) |
| — | `TEXT_MESSAGE_*`, `MESSAGES_SNAPSHOT`, reasoning events | Not used at R1–R2 (no chat, no reasoning shown) |

**Rules:**

- **Events never carry authority.** Approve, cancel, retry, resume, take over and raise budget are REST commands with `If-Match` and the version hash. After an event, the Studio re-reads what it shows from the API.
- **Tool-call events are summaries.** They carry the tool name, the source domain, the outcome and counts; never page text, prompts, model output, secrets or signed URLs (TH-20, TH-31).
- **The stream is scoped** to the caller's workspace and project like every route, and reconnects with the refreshed token (TH-08, TH-32).
- **Recovery.** `Last-Event-ID` resumes the stream; on any reconnect the server sends `STATE_SNAPSHOT` first. Nothing is ever replayed as an action.
- **Custom names** start with `opportunityos.` and are listed in the contract.
- **Pinned.** `ag-ui-protocol` (Python, api) and `@ag-ui/core` (web) are pinned in the M0 lockfiles. The protocol is pre-1.0, so an upgrade is its own spec.
- **Logged and replayable.** The relay logs each event with the trace ID; recorded streams in `contracts/examples/agui/` are replayed in Playwright.

## If chat drafting is promoted (R-64)

The full chat pipeline in PROCESS.md would apply:
- each user message becomes an AG-UI run request, with a closed intent list limited to drafting (edit the hook, rephrase a beat, suggest a scene change);
- every proposal becomes a revision request reviewed on S-09;
- there are no approval or publication intents.

Not designed now.
