# Agent architecture

Status: **Draft for G2** (Stage 2c addendum, 14 Nov 2026; Q-33–Q-35 decided). Applies the [Agent architecture](../PROCESS.md#agent-architecture) section of PROCESS.md to OpportunityOS. Baselined at G2; after that it changes only through change control.

Owners of related facts: containers, components, write path and revision graph [ARCHITECTURE.md](ARCHITECTURE.md) · task contracts [tasks.json](../contracts/agent-tools/tasks.json), [task-io.schema.json](../contracts/agent-tools/task-io.schema.json), [execution.schema.json](../contracts/agent-tools/execution.schema.json) · tools [tools.schema.json](../contracts/agent-tools/tools.schema.json) · AG-UI stream [agui/stream.json](../contracts/agui/stream.json) · threats [SECURITY.md](SECURITY.md#agent-risks-prompt-injection-excessive-agency-generated-code) · telemetry [OBSERVABILITY.md](OBSERVABILITY.md) · decisions ADR-003 (durable workflows), ADR-009 (adapters), ADR-010 (outbox), ADR-014 (model), [ADR-020](../adr/ADR-020-ag-ui-event-stream.md) (AG-UI), [ADR-021](../adr/ADR-021-agent-runtime-contract.md) (agent runtime) · owner decisions Q-33, Q-34, Q-35 ([QUESTIONS.md](../product/QUESTIONS.md)).

## Shape

OpportunityOS's agents are bounded workers inside durable workflows, not conversational assistants. At R1–R2:

- a person starts work with a structured command in the Studio; there is no chat (A-28; R-64 is Could);
- a DBOS workflow (ADR-003) runs a bounded agent task (research, script or storyboard) under a task contract (R-63);
- the result is a new **draft version** that a person reviews at a gate (A–E). An agent never approves, publishes or spends beyond its reservation (R-43, R-34);
- **routing is the workflow**, fixed in code; no model decides which agent runs;
- the Studio follows runs through **AG-UI events** on the project's event stream (ADR-020).

Everything else in production (demonstrations, narration, timing, compile, render, QA, revision impact, cost) is code with no model.

## Maturity per workflow

Maturity is assigned per workflow, from tested behaviour (PROCESS.md). Targets below were accepted as A-33 (Q-33, 14 Nov 2026). Intake is a structured form by design (A-28), so no workflow claims L2 conversation; the agent work aims at L3 reliability, with L4 features where the PRD asks for reviewer assistance and continuity.

| Workflow | Journey steps | Agent | Target R1–R2 | Later | Evidence before the level is claimed |
|---|---|---|---|---|---|
| Brief, destination, preflight | J1 steps 1–4 (S-01–S-04) | none | L1 form, code preflight | — | Valid brief versions; preflight blocks unbuildable briefs (R-07) |
| Research and claim review | J1 step 5 (S-05) | research | L3 execution, L4 reviewer assistance (claims side by side with sources and narration) | — | Golden research fixtures pass; every claim's excerpt found in its source; injection fixtures fail closed; one claim ledger per run, never duplicated after a restart |
| Script | J1 step 6 (S-06) | script | L3 | — | Every beat references input claims; target duration met; regenerated drafts never overwrite reviewed versions |
| Storyboard | J1 step 7 (S-07) | storyboard | L3 | — | VideoSpec passes the compiler or lists capability gaps; values come from demonstrations only |
| Narration, render, QA, package | J1 steps 8–9 (S-08, S-11) | none | L3-grade code path | — | QA-03, QA-04, QA-06 |
| Revision and recovery | J6 steps 1–4 (S-09, S-10, S-13, S-14) | script or storyboard, scoped to the target (Q-34) | L4: the agent redrafts only what was asked, impact before any render, continuity across versions and gates | — | KPI-03 (time to revise); no out-of-scope changes accepted; only changed artifacts rebuilt (R-32) |
| Publication record and metrics | J1 step 10 (S-12) | none | L1 manual, labelled manual | L3 connected publishing with reconciliation (R3) | QA-07 at R3 |
| Learning and slate | J3 (S-16, S-15), J2 and J4 at R3 | none at R1–R2 | L1 | L5 candidate: R-75 diagnostic recommendations, after A-18 | KPI-12: better than an editorial baseline, low alert burden |

## Journeys → agents

| Journey step | Screen | What runs | What it prepares | Who decides, where | R-xx, US-xx |
|---|---|---|---|---|---|
| J1 step 4 | S-03 | code: preflight, estimate | Feasibility, blockers, cost estimate | Owner approves Gate A on S-03 | R-06, R-07; US-02 |
| J1 step 5 | S-05 | **research** agent | Claims, sources, short excerpts, contradictions, unsupported gaps | Reviewer marks each claim on S-05 | R-08–R-10; US-03 |
| J1 step 6 | S-06 | code: demonstrations; **script** agent | Computed values; narration beats with claim references | Owner approves Gate B on S-06 | R-11–R-14, R-57; US-04, US-05 |
| J1 step 7 | S-07 | **storyboard** agent, compiler | VideoSpec from the capability catalogue, checked by the compiler | Owner approves Gate C on S-07 | R-16, R-18–R-22; US-06, US-08 |
| J1 step 8 | S-08 | code: TTS, alignment, captions, render | Narration take, timing, clips, master | Owner reviews on S-08 | R-25–R-30; US-07 |
| J1 step 9 | S-11 | code: QA, rubric, package | Findings, scores, package | Owner approves Gate D on S-11 | R-37–R-41; US-11, US-12 |
| J1 step 10 | S-12 | none (manual) | — | Publisher records upload; Gate E (R2) | R-46–R-48; US-13 |
| J6 step 1–2 | S-09, S-10 | **script** or **storyboard** agent, scoped; code: impact | A redraft of only the targeted beats or scenes; rebuild and reuse sets, cost, timing shifts, reopened gates | Owner applies on S-09; re-approves the reopened gate on S-06 or S-07, comparing on S-10 | R-31–R-33; US-09, US-11 |
| J6 step 3 | S-13 | code: retry, resume, takeover | Attempt history, error class, repair action | Owner retries, resumes or takes over | R-50–R-53; US-14 |

### How a revision reaches an agent (Q-34)

Revisions go through the agent (product-owner decision, 14 Nov 2026; R-31 AC3). Hand edits remain available on the draft.

1. **Request.** On S-09 the owner states the change in words against a target: a claim or beat (script) or a scene or object (storyboard). `RevisionRequest.mode` is `agent_redraft` by default.
2. **Scope preview, before any spend.** Code shows which agent will redraft which targets, its estimated cost and the gates likely to reopen (`RevisionImpact.stage = scope`).
3. **Redraft.** `POST /revisions/{id}/redraft` starts a `revision_redraft` run. The script or storyboard task gets the current approved version, the request and a `RevisionScope` with the target IDs. Its output is a new **draft** version. The acceptance stage rejects any change outside the targets (`out_of_scope_change`); a stale base is rejected as usual (C09).
4. **Full impact, before any render.** Code diffs the draft against the approved version and shows what rebuilds and is reused, cost, timing shifts (with the R-31 AC2 options) and the gates that reopen (`stage = full`). The owner can edit the draft by hand, run the redraft again, discard it, or apply.
5. **Apply.** Applying starts the `revision` workflow: TTS, captions, clips, assembly and mix for changed inputs only (R-32). The reopened gate is approved again on S-06 (Gate B) or S-07 (Gate C), then Gate D for the new master.
6. **History.** Every redraft is a new version; earlier versions and masters stay (R-33).

The PRD §10.3 example ("hold two seconds longer") is a scene target: the storyboard agent changes the hold in the VideoSpec, and code re-times the later scenes and captions.

## Planes → components

| Plane | OpportunityOS components | Notes |
|---|---|---|
| Interaction | `web` (Studio), `api.runs` (commands, AG-UI stream), outbox relay | AG-UI observe mode (ADR-020); approvals are REST commands |
| Control | `api.projects` (production state machine, R-44), `api.approvals`, `api.auth`, `api.cost`, `api.contracts` (preflight) | Guards and approvals in code (R-40–R-43) |
| Workflow | `wf.dispatcher`, `wf.production` on DBOS, `wf.budget` | Fixed graph per workflow type; DBOS queues bound concurrency |
| Agent harness | `agent.runner` with `agent.research`, `agent.script`, `agent.storyboard` | `AgentRuntime` interface (ADR-021); thin loop, no framework |
| Execution | `agent.tools` (tool host), adapters (ADR-009), render service, `wf.demonstrations` | Read-only tools; render on a private network with job limits |
| Context and evidence | PostgreSQL immutable versions, object store (ADR-007), `audit_log`, `outbox_event`, traces | Content hashes on every version; no vector store or shared memory |
| Assurance | Schema validation, compiler, postconditions, media QA, eval fixtures, CI | Deterministic hard gates (QA-01–QA-12) |
| Operations | Budgets (R-34), OpenTelemetry (ADR-016), retention (A-14, A-30), backups (NFR-14), kill switches | See OBSERVABILITY.md |

**State owners.**

| State | Owner here | Rule |
|---|---|---|
| Domain truth | `api.*` in PostgreSQL | Insert-only versions with SHA-256; `If-Match` on heads |
| Workflow and task state | DBOS system tables; `execution_run`, `task_attempt` as projections | Workflow ID = request ID; attempts unique per `(run, task_key, attempt)` |
| Agent scratchpad | `agent.runner`, inside one attempt | Never stored as truth; discarded after the attempt |
| Session | None at R1–R2 (no chat) | — |
| Shared memory | None | No memory across runs; each run reads current versions |
| Artifact | Object store, content-addressed, object lock on masters | Producer attempt and input hash recorded |
| UI projection | TanStack Query cache in `web`, fed by the AG-UI stream | Never used as a guard; commands re-check in the API |

## Lifecycle

The reference lifecycle maps onto the production state machine (R-44, owned by ARCHITECTURE.md) and run states (`execution_run.state`):

| Reference | OpportunityOS |
|---|---|
| CREATED → VALIDATED → PLANNED | Project `DRAFT`; brief version; preflight passes; Gate A approved |
| READY → EXECUTING | `workflow_request` written; run `pending` → `running`; project `RESEARCHING` or `PRODUCING` |
| WAITING_APPROVAL | Run `waiting_approval`; project `SCRIPT_REVIEW`, `STORYBOARD_REVIEW`, `FINAL_REVIEW` |
| BLOCKED / NEEDS_INPUT | Run `paused_budget`; project `BLOCKED` (budget, rights, capability) |
| VERIFYING | Schema, freshness and postcondition checks; media QA (`QA`) |
| RETRYING | A new `task_attempt` under the task's retry ceiling (R-51) |
| CANCELLING → CANCELLED | `cancel_requested_at` set (cancelling); run `cancelled` once in-flight steps settle and reservations are released (R-52) |
| FAILED | Run `failed`; project `FAILED`, then resume or takeover (R-51) |
| COMPLETED | Run `succeeded`; output is a draft version awaiting its gate |

Graph pattern: each workflow type is a fixed DAG of steps (research → script → storyboard; narration → per-scene clips in parallel → assembly → mix → QA). Per-scene clips join as **all required**. Loops exist only inside an attempt (model ↔ tools), bounded by the task budget. Agents cannot change the graph; `proposedGraphChanges` is always empty at R1–R2.

## Execution contract

The four reference schemas map to these contracts (ADR-021, contracts 0.3.0):

| Reference | OpportunityOS | Where |
|---|---|---|
| `TaskContract` | Static part per task type: tools, budget, retry ceiling, timeout, failure states, postconditions, output disposition and reviewing gate. Per-attempt part: run, attempt, idempotency key, input bindings (version ID + hash), data classification | [tasks.json](../contracts/agent-tools/tasks.json); `TaskContract` in [execution.schema.json](../contracts/agent-tools/execution.schema.json) |
| `ContextEnvelope` | The exact input versions and hashes read, the task input, remaining budget, prompt version | `ContextEnvelope` in execution.schema.json; input bodies in [task-io.schema.json](../contracts/agent-tools/task-io.schema.json) |
| `AgentResult` | Status, output reference (the new draft version), evidence references, validation results per stage, budget consumed, failure category. `proposedActions` and `proposedGraphChanges` are always empty | `AgentResult` in execution.schema.json |
| `ExecutionEvent` | `DomainEvent` with workspace, project, actor, subject, correlation (run) and causation IDs, trace, and `seq` from the outbox (per-workspace monotonic) | [domain-event.schema.json](../contracts/events/domain-event.schema.json), `outbox_event.seq` |

Reference event names map to domain event types: `RunCreated` → `workflow.requested`; `TaskDispatched`, `AgentStarted` → `task_attempt.started`; `ModelInvoked`, `ToolRequested`, `ToolAuthorized`, `ToolCompleted` → spans and summarised `TOOL_CALL_*` (not domain events); `ArtifactProduced`, `TaskResultProposed` → the version-created events; `TaskAccepted` → `approval.recorded`; `TaskRejected` → approval returned; `TaskFailed`, `TaskCancelled` → `task_attempt.finished` with its error class, `run.state_changed`.

## Agent harness (ADR-021)

`agent.runner` implements the provider-neutral `AgentRuntime` interface as a thin loop over the `LlmProvider` adapter. No agent framework at R1–R2.

| Method | Here |
|---|---|
| `start(contract, envelope)` | Called from a DBOS step; returns the attempt ID and emits `task_attempt.started`; changes no project state |
| `resume(checkpoint, signal)` | DBOS recovery of the workflow from its last completed step; a model-call step restarts as a new attempt; tool results within an attempt are not replayed as effects (tools are read-only) |
| `interrupt(run, reason)` | Budget pause (`paused_budget`) or wait for a gate (`waiting_approval`) |
| `cancel(run, command)` | `POST /runs/{id}/cancel`; the next step transaction sees `cancel_requested_at` and stops |
| `inspect(run)` | `GET /runs/{id}` and attempts (R-50), secrets and page text redacted |
| `subscribe(run, cursor)` | The project AG-UI stream with `Last-Event-ID` (ADR-020) |

There is no delegation at R1–R2: no task starts a child agent, so every contract's child budget is 0.

## Context and validation

- **Envelope.** Each attempt reads the head versions it needs, records their IDs and hashes in the envelope, and builds the task input from them only: research reads the brief and operator source URLs; script reads reviewed claims and demonstrations; storyboard reads the approved script, demonstrations, capability catalogue and brand kit. A revision redraft also binds the approved base version and the revision note (`revision_note` role).
- **No memory** carries between runs. Summaries are never used as inputs; inputs are versioned records.
- **Stale results (C09).** Before the result is stored, the step transaction re-reads the head hashes of every bound input. If any changed, the result is rejected with `stale_input` and the operator sees "inputs changed during the run; run again".

**Three validation stages** (failure states in tasks.json):

1. **Schema:** Pydantic output model from task-io.schema.json → `schema_invalid`.
2. **Policy and freshness:** input bindings still current, run not cancelled, budget reservation held, tool calls inside the allowlist → `stale_input`, `budget_exhausted`, `injection_detected`.
3. **Acceptance:** postconditions in code (citations, claim references, compiler validation, revision scope) → `citation_invalid`, `unknown_claim_reference`, `spec_invalid`, `capability_gap`, `out_of_scope_change`.

*Produced* = the model's output. *Verified* = passed all three stages and stored as a draft version. *Accepted* = a person approved it at its gate. Only accepted versions feed later gates and publication.

## Tools and external effects

**Tool host** (`agent.tools`) runs each call in the reference order: read current state, check the tool is in `permittedTools` and within budget, execute, record a summary (tool, host, counts, outcome) on the attempt span and the AG-UI stream. All agent tools are read-only (TH-13).

| External effect | Idempotency | Ambiguous outcome |
|---|---|---|
| LLM call (paid) | Attempt ID; result stored by attempt | Treated as failed; a retry is a new attempt and new reservation |
| TTS call (paid) | Request keyed by text, voice and settings hash | Re-request is safe; the take is stored by hash |
| Source fetch | SSRF guard, allowlist from search results (TH-12, TH-14) | Read-only; retried within budget |
| Render job | `jobId` = effective input hash; lease-based claim in the render service | Poll status; never start a second job for the same hash |
| Publication | Manual at R1–R2: the operator uploads and records the URL | R3: `PUBLICATION_UNKNOWN` and reconcile before any new write (R-69) |

**Failure classes** map to the error classes the Studio already shows (R-53):

| Reference class | `ErrorClass` | Response |
|---|---|---|
| Provider or model error, timeout | `retryable_provider` | Retry with backoff up to the ceiling |
| Malformed or invalid output | `invalid_content` | Retry with validation errors, then fail with the failure state |
| Deterministic render defect | `render_defect` | No retry; named scene and object; edit or take over |
| Ambiguous external effect | `uncertain_external` | Reconcile first |
| Stale input | `conflict` | Reject; run again on current versions |
| Policy denial | `authorization` | Stop; no retry |
| Budget exhausted | `resource_limit` | Pause for budget; raise allowance or cancel |
| Worker crash | (recovered, not shown) | DBOS resumes; new attempt |

**Fencing.** A late attempt cannot overwrite accepted work: results are keyed by attempt, heads move only with `If-Match` on `row_version`, and the step transaction re-checks cancellation and input hashes before writing.

## Approvals and trust

- **Binding.** Gate approvals record the actor, responsibility, gate, target, version, SHA-256, scope, destination, the evidence shown and the policy versions in force: brand kit, rubric and content policy (R-41, Q-35). A target change makes the approval non-current. A rubric or content-policy change reopens Gate D for unpublished packages (`policy_changed`). A Gate E approval for a scheduled release lapses if the time passes with no recorded publication (`release_time_lapsed`). There is no other time expiry.
- **Untrusted content.** Fetched pages, search results and model output are data. They never reach a command, a URL fetch outside the allowlist or an approval (TH-12–TH-15). Model output is typed data; nothing it writes is executed (NFR-05).
- **Tenancy.** One workspace at R1, but `workspace_id` is on every row, enforced by row-level security, carried on events and the stream (NFR-04).

**Budgets.** Each attempt reserves its estimated cost before dispatch, under a row lock, including parallel clips (R-34). Task ceilings in tasks.json cap calls and tokens. When a reservation fails, the run pauses with `paused_budget` and the stream says which action unblocks it.

**Models and prompts.** One model at R1 (ADR-014) behind `LlmProvider`. Each attempt stores provider, model, prompt SHA-256 and tool versions (R-50). Prompts live in `agent/prompts/<task>.md` and change only through a spec with its evals. No fallback model at R1; a provider outage is `retryable_provider`, then a paused run.

## AG-UI in OpportunityOS

Decision: [ADR-020](../adr/ADR-020-ag-ui-event-stream.md). Contract: [agui/stream.json](../contracts/agui/stream.json). Examples: [examples/agui/](../contracts/examples/agui/).

**How we use it.** One SSE stream per open project, `GET /projects/{projectId}/events`, carries AG-UI events encoded with the AG-UI SDK. The thread ID is the project ID; the run ID is the execution run ID. Runs are started by REST commands and observed on the stream, because production runs are durable and outlive the browser. Each SSE `id:` is the outbox `seq`, used as the resume cursor.

| Source | AG-UI event | What the Studio does |
|---|---|---|
| Connect or reconnect | `STATE_SNAPSHOT` (active runs, current step, waiting and blocked reasons with their unblock action) | Rebuilds the run indicator; then applies events after the cursor |
| Run starts | `RUN_STARTED` | Run indicator appears |
| Run succeeds | `RUN_FINISHED` | Indicator clears; affected queries refresh |
| Run fails or is cancelled | `RUN_ERROR` with `code` = error class | Error panel with the matching repair (R-53) |
| Workflow step or task attempt | `STEP_STARTED`, `STEP_FINISHED` | "Step 3 of 4" in the run indicator and S-13 |
| Agent tool call | `TOOL_CALL_START`, `_ARGS`, `_END`, `_RESULT`, as summaries | S-13 attempt timeline, e.g. "fetched 5 sources, 1 refused" |
| Render progress; pauses for budget, approval or takeover | `ACTIVITY_SNAPSHOT`, `ACTIVITY_DELTA` | Per-scene progress; "waiting for Gate C", "paused for budget: raise allowance" |
| Every domain event | `CUSTOM` `opportunityos.<type>` carrying the DomainEvent | TanStack Query invalidation (ADR-018) |
| — | `TEXT_MESSAGE_*`, `MESSAGES_SNAPSHOT`, `STATE_DELTA`, reasoning events | Not used at R1–R2 |

**Rules:**

- **Events never carry authority.** Approve, return, cancel, retry, resume, take over, redraft, apply and raise budget are REST commands with `If-Match` and the version hash. After an event, the Studio re-reads what it shows.
- **Waiting is legible.** A run waiting for a gate shows an `opportunityos.run_paused` activity with `awaiting_approval` and the gate; the decision is made in the approval dialog, never from the stream.
- **Redacted summaries.** Tool-call events carry the tool, the source host, the outcome and counts; never page text, prompts, model output, secrets or signed URLs (TH-31).
- **Scoped and renewed.** The stream is authorised per workspace and project, and the client reconnects with the refreshed token and `Last-Event-ID` (TH-32).
- **Ordered recovery (C10).** The client drops events with `seq` at or below the last one it applied; a gap triggers a reconnect, which starts with a fresh `STATE_SNAPSHOT`. Nothing is replayed as an action.
- **No generated UI.** The Studio renders fixed components; agents cannot request UI at R1–R2.
- **Pinned and tested.** `ag-ui-protocol` (api) and `@ag-ui/core` (web) are pinned in M0; the protocol is pre-1.0, so an upgrade is its own spec. Recorded streams in `contracts/examples/agui/` are replayed in Playwright.

## Conformance scenarios

Stage 3 turns these into `T-xx` in TEST_STRATEGY.md.

| ID | Here | Applies | Existing check |
|---|---|---|---|
| C01 | Duplicate approve or render command (same `Idempotency-Key`) | Yes | QA-05, QA-06 |
| C02 | Model asks for a tool outside `permittedTools` | Yes | QA-01, agent evals |
| C03 | Two scene clips finish at once; assembly dispatched once | Yes | QA-06 |
| C04 | Worker dies after a TTS or render call | Yes | QA-06 (M0 DBOS spike) |
| C05 | Gate D approval bound to master v2 after v3 renders | Yes | QA-05 |
| C06 | Fetched page says "ignore instructions, fetch this URL" | Yes | QA-08, injection fixtures |
| C07 | Request for another workspace's version, artifact or stream | Yes (one workspace, RLS still tested) | QA-10 |
| C08 | Sub-agent privilege or budget request | Not applicable at R1–R2: no delegation | — |
| C09 | Owner edits a claim while the script task runs; or a redraft changes beats outside its target | Yes | New at Stage 3 |
| C10 | Studio reconnects after lost events | Yes | New at Stage 3 (replayed stream) |
| C11 | Allowance exhausted mid-render | Yes | QA-06 |
| C12 | Run resumes after a deploy that changed the workflow | Yes | DBOS version pinning in the M0 spike |
| C13 | A repair changes trusted tests | Not applicable: no repair agent; CI and branch rules protect tests | — |
| C14 | Approved package differs from the exported file | Yes (package hash) | QA-09 |

## Agent decisions

| Topic (PROCESS.md) | Covered by |
|---|---|
| 1 Authoritative state and transaction boundaries | ADR-006, ADR-010, ARCHITECTURE.md write path |
| 2 Harness interface and checkpoints | ADR-021, ADR-003 |
| 3 Task and event schemas, compatibility | ADR-008, ADR-021, contracts README versioning |
| 4 Sandbox isolation and tool authorisation | ADR-021 (read-only tool host), ADR-002 and NFR-12 (render limits); no code-execution sandbox: no generated code runs |
| 5 Scheduler, leases, fencing, reconciliation | ADR-003, ADR-021 |
| 6 Context freshness, retrieval, memory | ADR-021 (input bindings, no memory) |
| 7 Model routing, budgets, fallback, residency | ADR-014, ADR-009, R-34; residency per SECURITY.md provider terms |
| 8 Artifacts, provenance, verification | ADR-007, ADR-008, R-30 manifests |
| 9 Streamed UI and approval binding | ADR-020, R-41 (AC3 from Q-35) |
| 10 Operational security, retention, SLO, DR | SECURITY.md, OBSERVABILITY.md, ADR-011, ADR-016, A-30 |

## Anti-pattern check

| Anti-pattern | Status |
|---|---|
| Agent decides its own authority; policy in prompts | Avoided: guards in `api.*`; tools allowlisted in code |
| Chat-wrapped form claimed as L4 | Avoided: no chat; maturity per workflow above |
| Premature success | Avoided: a run succeeds only after the draft version is stored; publication only when verified (R-46) |
| Silent derivation | Avoided: numbers come from demonstrations (`valueRef`); unsupported claims are gaps |
| Blind retry after timeout | Avoided: idempotent keys; reconcile at R3 |
| Token-stream-only frontend | Avoided: typed AG-UI events plus snapshots |
| Framework state as product state | Avoided: no framework; DBOS tables are projected, not exposed |
| Self-reported "all green" | Avoided: compiler, media QA and gates are independent of the agents |

## Adding an agent task

Each new task is a spec (`SPEC-xx`) and needs an `R-xx` that asks for it.

1. Record the workflow's target maturity level here and in the stories.
2. Add the task to `tasks.json` (tools, budget, retries, timeout, failure states, postconditions, output disposition, reviewing gate) and its input and output to `task-io.schema.json` (contract minor version).
3. Reuse or add read-only tools in `tools.schema.json` and list them in `permittedTools`.
4. Write the prompt in `agent/prompts/<task>.md`, versioned; each attempt records the prompt hash.
5. Add the command and workflow type that starts it (`openapi.yaml`, `workflow-request.schema.json`) and its step in `wf.production`, with budget reservation and the retry ceiling.
6. Check the three validation stages in code and map every failure state to an error class (R-53).
7. Store the output as a new draft version and name the gate that reviews it.
8. Add its step names, tool-call summaries and activity types to `agui/stream.json`, and its Studio surface on the design canvas.
9. Add tests: eval fixtures in `agent/evals/<task>/` (valid, invalid, injection, stale input), mocked unit tests, the conformance scenarios that apply, and a recorded AG-UI stream replayed in Playwright.
10. Add telemetry (spans, `oos.agent.*` metrics), its rows in the tables above, and its row in `STATUS.md`.

## If chat drafting is promoted (R-64)

Chat would be an L2–L3 drafting surface, not a new authority. Each message would be an AG-UI run request with a closed intent list limited to drafting (edit the hook, rephrase a beat, suggest a scene change); every proposal becomes a revision request reviewed on S-09; there are no approval, spend or publication intents. Not designed now.
