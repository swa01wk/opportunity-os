# Product Delivery Process

Nov 12, 2026 · @Swaroop Shivakumar

## Purpose and principles

This process takes a client or product-team PRD to a released product one milestone at a time. Cursor implements the code, CI and Claude review it, and a human approves every merge. It fits products with a backend, a frontend and, for agentic products, AI agents (see Agent architecture).

1. **The PRD is input, owned by the product owner.** Store it in `docs/sources/` and derive your own `REQUIREMENTS.md` from it. It changes only when the product owner decides: during discovery (until G3) it may be revised in place with a dated revision note; after that, through change control.
2. **One owner per fact.** Each requirement, decision or threshold lives in one doc; other docs link to it.
3. **Traceable IDs end to end.** PRD section → `R-xx` → component, screen S-xx and `ADR-xxx` → `SPEC-xx` → `T-xx`.
4. **Decisions are recorded when made**, as ADRs, not as a later stage.
5. **Contracts before code.** API, event, agent task and AG-UI schemas are agreed before backend, frontend and agent work splits.
6. **Shift left.** Test harnesses, security checks and observability are built in M0, not added at the end.
7. **Small, reversible changes.** One spec = one short-lived branch = one PR.
8. **AI writes, humans own.** AI review assists; a person is accountable for every merge.
9. **`STATUS.md` is the single entry point** for anyone asking where the product stands.

## Lifecycle at a glance

There are seven stages, each closed by a gate. Stages 1–3 run once per product and again for each change request. Stages 4–6 repeat for every milestone.

| # | Stage | Question it answers | Owning docs | Gate |
| --- | --- | --- | --- | --- |
| 1 | Intake | Who is it for, what does it solve, and what exactly must we build? | Product framing in the PRD or `REQUIREMENTS.md`, `REQUIREMENTS.md`, `QUESTIONS.md`, `DISCOVERY.md` | G1 Requirements baseline signed off |
| 2 | Design | How will it work? | `ARCHITECTURE.md`, `AGENT_ARCHITECTURE.md` (agentic products), ADRs, contracts, `UI_DESIGN.md`, Claude Design canvas, screens (docs/design/), `TECH_STACK.md`, `SECURITY.md`, `OBSERVABILITY.md` | G2 Design review passed, screens approved |
| 3 | Plan | In what order, and how do we prove it? | `DEVELOPMENT_PLAN.md`, `TEST_STRATEGY.md`, `DELIVERY_PLAN.md` | G3 Milestone scope and dates agreed |
| 4 | Build | What is being built now? | `plans/Mx/specs/`, PRs, `STATUS.md` | Each spec meets its Definition of Done |
| 5 | Verify | Does the milestone meet the requirements? | E2E and eval reports, UAT notes | G4 Milestone exit checklist met |
| 6 | Release | Is it safe to ship and run? | `RELEASE_NOTES.md`, `CHANGELOG.md`, `RUNBOOK.md` | G5 Go-live approved |
| 7 | Learn and change | What changes next? | `plans/retros/`, change requests | Changes re-enter at stage 1 |

**Gate owners.** Every gate names who signs it, and `STATUS.md` records each approval with its date:

- G1: the client's product owner and your tech lead;
- G2: your tech lead for the design, the client for the screens;
- G3: the client for scope and dates;
- G4: the client for UAT, your tech lead for the checklist;
- G5: the client and whoever will run production.

## Stage 1 — Requirements intake

The first output is your own requirements baseline, derived from the PRD and confirmed by the client before any design starts.

**Inputs:** the PRD (versioned in `docs/sources/`, revised only by the product owner), any client designs, and access to existing systems.

**Product framing first.** Before writing requirements, make sure the product concepts below exist, because requirements, screens and tests all trace back to them. Keep the PRD's own IDs where it has them; where it lacks one, propose it in `REQUIREMENTS.md` and raise a `Q-xx`.

- **Personas** (`P-xx` or the PRD's IDs): who uses the product, their job, difficulties and what success means. Personas are not roles.
- **User journeys** (`J-xx`): trigger, sequence of steps, branches and outcome, each with its release.
- **User stories** (`US-xx`): "As <persona>, I want <capability> so that <outcome>", with release, journey and acceptance.
- **Agent steps** (agentic products): for each journey step an agent performs, what it prepares, the human decision it feeds, and the target maturity level L1–L5 (see Agent architecture).
- **Value and defensibility**: the problems the product solves, how each is solved and the evidence that proves it; and the moat hypotheses, in the order they would be earned, each with its proof checkpoint. These are hypotheses, never claims, until their proof is met.

1. Break the PRD into atomic requirements:
   - functional `R-xx`;
   - non-functional `NFR-xx`: performance, security, availability, accessibility, languages, compliance, AI quality.
2. Give each requirement its PRD section, a priority (Must, Should, Could, Won't) and acceptance criteria in Given / When / Then form.
3. Group requirements into features `F-xx`. Features become specs in stage 3.
4. Log every gap or ambiguity as `Q-xx`, with the assumption `A-xx` you will build on if nobody answers.
5. If an existing system is involved, write `DISCOVERY.md`: current behaviour, integration points, constraints.
6. Record the PRD's success metrics as `KPI-xx`, each with a target and how it will be measured. They become analytics events in stage 2 and are reviewed after release.

**Outputs:** `REQUIREMENTS.md`, `QUESTIONS.md`, and `DISCOVERY.md` when needed.

**Gate G1:**

- personas, journeys, stories and the value and defensibility hypotheses exist and the client has confirmed them;
- every user-facing Must `R-xx` traces to a user story and its journey;
- for agentic products, every agent step has a target maturity level and names the person who approves its output;
- every PRD section maps to at least one `R-xx` or is listed as out of scope;
- every Must has acceptance criteria;
- the client has answered the questions or accepted the assumptions.

## Stage 2 — Design

Design produces the architecture and its decisions together. Then come the contracts that let backend, frontend and agent work proceed in parallel. Docs at the same step can be written at the same time.

| Step | Doc | Contents | Done when |
| --- | --- | --- | --- |
| 1 | `ARCHITECTURE.md` | Context, containers and components (C4 levels 1–3), data model, write path, migration of any existing data, quality scenarios for each NFR | Every `R-xx` maps to a component |
| 1 | `AGENT_ARCHITECTURE.md` | For agentic products: maturity per workflow, planes mapped to components, journeys → agents, lifecycle, execution contract, harness, tools and effects, approvals, AG-UI, conformance scenarios (see Agent architecture) | Every agent step maps to a contract, a component and an approval; the ten agent decisions have ADRs or links |
| 1 | `docs/adr/ADR-xxx.md` | One ADR per significant choice, written when the choice is made | No open choice blocks M0 |
| 2 | `docs/contracts/` | OpenAPI spec, event schemas, agent task, result and tool schemas, the AG-UI contract (`agui/`), DB schema draft | Backend, frontend and agent can each mock the others |
| 3 | `UI_DESIGN.md` | Journeys in scope and their steps, the stories and problem each screen serves, screens, flows, empty / loading / error states, accessibility, languages | Every user-facing `R-xx` and every in-scope journey step maps to a screen |
| 3 | `TECH_STACK.md` | Tools and versions per layer, each linked to its ADR; a monthly cost estimate for infrastructure and model usage | Every layer has a chosen tool |
| 4 | `SECURITY.md` | Threat model (STRIDE), auth and roles, data classification, secrets, personal-data handling and retention under the applicable law (for example India's DPDP Act or GDPR); for agents, prompt injection, excessive agency, tenant crossover, stale results and stream leakage | Threats have mitigations or accepted risks |
| 4 | `OBSERVABILITY.md` | Signals per component, SLOs (including time to first event for agent runs), alerts, retention, PII redaction, product analytics events for each KPI-xx | Every key journey has an SLO |

**Screens (step 5, after `UI_DESIGN.md`).** Screens are designed by journey in Claude Design, reviewed there by the client, then committed to the repo as HTML prototypes. Cursor later rebuilds them as production code, so the approved screens are the visual source of truth for every frontend spec.

1. **Design in Claude Design.** One canvas per screens version, using `docs/design/tokens.md`:
   - a page mapping journeys → steps → stories → screens, and what is out of scope;
   - a page on what the product solves: problems → screens → `KPI-xx`, and the moat hypotheses with their proof checkpoints;
   - one page per journey, screens in step order, joined by links so the client can click through each journey in Play;
   - under each screen, a note naming its journey step, stories, gate, `R-xx`, the problem it solves, the moat it builds and the states still to come.
2. **Client review on the canvas.** The client comments on the canvas; screens are revised there until approved. `STATUS.md` links the canvas.
3. **HTML in the repo.** Each approved screen is built as a self-contained HTML prototype that matches the canvas, with realistic synthetic data and its empty, loading and error states.

- Each screen gets an ID `S-xx`, listed in `UI_DESIGN.md` with its journey step, stories, `R-xx` and file path (`docs/design/screens/S-xx-<name>.html`).
- Each prototype shows realistic sample data and its empty, loading and error states.
- Shared colours, type and spacing go in `docs/design/tokens.md`, so every screen and every Cursor run uses the same values.
- Screens go through the normal loop: a `design/screens-<version>` branch, a PR, client review, then merge.
- `STATUS.md` tracks each screen: Draft → Client review → Approved → Built. Once approved, a screen changes only through change control.

The trace for UI work is `J-xx` / `US-xx` → `R-xx` → `S-xx` → frontend `SPEC-xx` → Playwright `T-xx`.

**Gate G2 (design review):**

- traceability is complete;
- contracts are versioned;
- the threat model is reviewed and the client has approved the screens on the canvas, journey by journey;
- for agentic products, the agent review checklist (see Agent architecture) passes;
- the HTML prototypes match the approved canvas;
- nothing is designed that no requirement asks for.

## Agent architecture

Most products built with this process are agentic: AI agents interpret what a person needs, gather and prepare work, and a person approves anything consequential. For these products Stage 2 also writes `docs/architecture/AGENT_ARCHITECTURE.md`, which applies this section to the product. This section is generic and holds for every agent unless an ADR says otherwise. It follows three references: the Agentic Application Reference Architecture (v1.2), its Engineering Practices Guidebook (v1.0) and the Agent Capability Maturity Framework.

**Operating principle.** Agents recommend and prepare; deterministic systems enforce rules and transitions; authorised humans approve consequential decisions. Model output is never the source of truth for permissions, business rules, workflow state or approval.

**Golden rules:**

1. **Separate authority from intelligence.** The model proposes; a deterministic control plane authorises. Generated text never authorises a state transition.
2. **Start deterministic.** Use normal code for fixed transformations, routing and policy. Use a model only where adaptive judgement adds value.
3. **Contract in, evidence out.** Every agent run receives a versioned task contract and a context envelope, and returns a typed result with evidence. A model completion never completes a task by itself.
4. **Bound all autonomy.** Every run has limits on steps, model and tool calls, tokens, cost, time, retries and child agents, plus a defined stop behaviour.
5. **People approve consequential actions,** bound to the exact action and artifact version. Agents never approve.
6. **Untrusted by default.** User input, tool output, retrieved pages, files and model output are data, never instructions.
7. **Durable and recoverable.** A crash, timeout or duplicate event never loses accepted work or repeats an external effect.
8. **Auditable and observable.** Every consequential action links objective, actor, contract, inputs, model and tools, artifacts, checks and outcome.
9. **Modular first.** Start with a modular monolith, workers and PostgreSQL with an outbox. Split services or add an orchestration platform only when an ADR shows the need.

### Maturity: what the agent promises, per workflow

Maturity is assigned per workflow and capability, not once for the product. A product can hold an L3 workflow beside an L1 form. Claim a level only from tested behaviour, never from a demo or the model's sophistication. Build reliable L3 first, then L4 features that remove rework, then L5 only around well-observed events.

| Level | Promise | The system must | Exit evidence |
| --- | --- | --- | --- |
| L1 Structured self-service | Digitise intake | Collect and submit fields through a form | Valid submissions with a retrievable reference |
| L2 Conversational self-service | Make intake conversational | Carry the same form semantics in chat, including corrections | Conversation completion, fallback rate |
| L3 Intent-aware task execution | Execute the task | Route intent; extract several fields at once; resolve entities; reuse verified context; ask only for what is missing; validate in code; keep durable drafts; confirm before submitting; execute idempotently; audit and recover | Representative tasks complete once, correctly, even after interruption; idempotency and audit evidence |
| L4 Context-aware outcome ownership | Own the outcome (assist and track, never approve) | Assemble verified context with provenance; separate facts from assumptions; brief reviewers; keep continuity across handoffs and sessions; reduce rework; report status and the next owner | Measured drop in requester and reviewer effort, incomplete submissions and rework; no unauthorised action |
| L5 Proactive workflow productivity | Optimise the process | React to authorised events; recommend ranked next actions; prepare work; coordinate owners; act alone only on pre-authorised low-risk actions; throttle notifications; learn through governed releases | Better cycle time, backlog or SLA adherence without alert burden, leakage or hidden automation |

Stage 1 records the target level for each workflow, and `AGENT_ARCHITECTURE.md` records the level each workflow has reached.

### Planes and owners

Each responsibility has one owner. `AGENT_ARCHITECTURE.md` maps each plane to the product's components.

| Plane | Owns | Never |
| --- | --- | --- |
| Interaction | API commands, the event stream to the UI (AG-UI), sessions, approval capture, UI projections | Treats a UI command as authoritative before server-side validation |
| Control | Domain lifecycle state machine, guards, policy, authorisation, approvals, contracts | Delegates a permission decision to a model |
| Workflow | Task graph, readiness, scheduling, joins, retries, leases | Dispatches before dependencies and guards hold |
| Agent harness | Bounded model–tool loop, context assembly, checkpoints, delegation | Commits canonical state or declares a protected transition |
| Execution | Tool gateway, adapters, sandboxes, credentials broker | Runs a tool call that the gateway has not authorised |
| Context and evidence | Versioned artifacts, provenance, memory, event log, traces | Silently overwrites verified or superseded evidence |
| Assurance | Schema, policy and acceptance checks, evals, independent verification | Lets an agent edit the criteria that judge it |
| Operations | Budgets, quotas, telemetry, SLOs, recovery, kill switches, releases of prompts, models and policies | Changes behaviour without a versioned release |

**State owners.** Each kind of state has one owner and one consistency rule.

| State | Owner | Rule |
| --- | --- | --- |
| Domain truth | Control plane | Transactional, versioned updates |
| Workflow and task state | Orchestrator | Optimistic version per aggregate; fenced attempts |
| Agent scratchpad | Harness | Checkpointable, never authoritative |
| Conversation or session | Interaction service | Turn ordering, redaction, replay cursor |
| Shared memory | Context service | Verified facts only, with owner, revision and source |
| Artifact | Artifact store | Content hash, immutable version, producer and inputs |
| UI projection | Read model | Eventually consistent; never used as a guard |

### Lifecycle and execution graph

**Lifecycle.** Domain work moves through an explicit state machine. The product's own states map to this reference:

```
CREATED → VALIDATED → PLANNED → READY → EXECUTING → VERIFYING → COMPLETED
                                          ├→ WAITING_APPROVAL → EXECUTING
                                          ├→ BLOCKED / NEEDS_INPUT
                                          ├→ RETRYING → EXECUTING | FAILED
                                          └→ CANCELLING → CANCELLED
```

- Transitions are transactional, authorised, idempotent and recorded with actor, event, reason, time and evidence.
- Long-running work runs outside the transition's database transaction.
- Every task in a graph also has its own finer status.

**Execution graph.** Use the simplest pattern that fits: a DAG for dependent work, an explicit sub-workflow with an exit condition for loops, a hierarchical state machine for nested stages, and a saga with compensations for multi-system writes.

- Readiness is computed in code: a task dispatches only when its required parent outputs and current approvals exist.
- Joins are explicit: all required, quorum, first success, optional or human-decided. Never implied.
- A graph change (including one an agent proposes) is a versioned revision, validated for cycles, stale dependencies, permissions, fan-out and budget before it applies.
- Waits for a person are durable, outlive workers, and model expiry and revocation.
- Every loop has a progress test, a stop condition and an escalation.

### The execution contract

The contract between orchestration and agents is versioned in `docs/contracts/` like any other. The field names below are the reference; a product may rename them, mapping each in `AGENT_ARCHITECTURE.md`.

| Schema | Holds |
| --- | --- |
| `TaskContract` | Objective; immutable input references and dependency versions; allowed tools; permission scope; data classification; budget (tokens, cost, time, retries, children); expected outputs; acceptance checks; approval policy; idempotency key; provenance requirements |
| `ContextEnvelope` | The authorised, decision-specific snapshot given to the model: current state, contract, relevant artifact excerpts, recent tool observations, provenance, remaining budget |
| `AgentResult` | Status; output and evidence references; proposed actions and graph changes; budget consumed; failure category |
| `ExecutionEvent` | Event ID, schema version, type, time; tenant, run, task and attempt IDs; actor; correlation and causation IDs; per-aggregate sequence; contract version and graph revision; artifact references; payload by reference or redacted summary |

Reference event types: `RunCreated`, `TaskDispatched`, `AgentStarted`, `ModelInvoked`, `ToolRequested`, `ToolAuthorized`, `ToolCompleted`, `ArtifactProduced`, `ApprovalRequested`, `TaskResultProposed`, `TaskAccepted`, `TaskRejected`, `TaskFailed`, `TaskCancelled`. Events are published through the transactional outbox; consumers handle at-least-once delivery and dedupe by event ID.

### Agent harness

The harness is a bounded execution engine called with a `TaskContract`. It does not own workflows, authorisation or release state. Frameworks (LangGraph, OpenAI Agents SDK, Claude Agent SDK or a thin custom loop) sit behind one provider-neutral interface and are adopted only after the conformance tests pass. Framework-specific sessions, memory and checkpoints stay private to the adapter.

| Method | Guarantee |
| --- | --- |
| `start(contract, envelope)` | Returns run and attempt IDs and an event stream; makes no domain transition |
| `resume(checkpoint, signal)` | Resumes from a checkpoint with an authorised signal; never silently repeats an effect |
| `interrupt(run, reason)` | Checkpoints and enters an explicit stopped or waiting state |
| `cancel(run, command)` | Records cancellation intent and fences the worker and its children |
| `inspect(run)` | Status, artifacts, trace and evidence for an authorised requester, secrets redacted |
| `subscribe(run, cursor)` | Ordered per-run events from a resume cursor |

- **Checkpoints** sit at bounded step boundaries. Privileged actions are never replayed automatically.
- **Delegation is attenuated.** A sub-agent receives a typed work assignment and can never exceed its parent's tools, scope or budget; the parent waits through an explicit join. Sub-agents report facts and blockers, not their whole context.
- **No invented authority.** An agent cannot invent tools, raise its own policy, commit canonical artifacts or declare a protected transition.

### Context and the inference boundary

- **Fresh envelope per inference.** A context assembler reads only authorised, relevant, current state and artifact excerpts, and records the versions it read. It refreshes when an input or policy changes materially.
- **Facts versus summaries.** Summaries are lossy and may be stale. Requirements, approvals, blockers, critical failures and tool constraints stay in durable stores and are never dropped by compression.
- **Memory has rules:** write authority, conflict resolution, expiry, tenant boundaries and deletion are specified before any memory is shared between runs or agents. There is no shared mutable global memory.
- **Stale results.** If an input the envelope read changes while the model runs, the result is rejected or revalidated for the affected scope.

**Three validation stages,** run in order on every result, each with its own failure state:

1. **Schema:** shape, types, enums and references.
2. **Policy and freshness:** authorisation, scope, and that the inputs are still current.
3. **Acceptance:** the contract's acceptance checks, in code where possible.

A result is *produced* by the agent, *verified* by these checks and *accepted* by the control plane or a person. Only accepted results change canonical state.

### Tools, sandboxes and external effects

**Tool gateway.** Every tool is a typed adapter with input and output schemas, an auth requirement, a risk tier, a timeout, a retry policy and a receipt policy. Each call runs in this order:

1. read authoritative current state (not the prompt's snapshot);
2. authorise actor, tenant, task, action, target and context; deny before any effect, and record the decision;
3. reserve budget;
4. execute with an idempotency key, using a short-lived, action-scoped credential;
5. record the receipt, argument hashes, target versions and resulting artifacts as evidence.

- **Credentials** come from a broker, never from prompts, persisted arguments, screenshots or unredacted traces.
- **Sandboxes** for code, browser or terminal work are per task: isolated filesystem, egress rules, CPU, memory, disk and time limits, a pinned image, an ephemeral identity, and cleanup that keeps only allowed evidence.
- **Write model.** Observe read-only → propose → write a candidate → verify → promote by policy. Candidates are never canonical until promoted.
- **Ambiguous effects.** After a timeout on an external write, look up the receipt and reconcile before any retry. Never repeat a create, merge, send, publish or deploy blindly.

**Failure classes.** Each failure is classified, and the class decides the response:

| Class | Response |
| --- | --- |
| Provider or model error, tool timeout | Retry with backoff up to the ceiling |
| Malformed or invalid output | Retry with the validation errors, then fail with the failure state |
| Ambiguous external effect | Reconcile first; never retry blindly |
| Stale input | Reject the result; revalidate the affected scope |
| Policy denial | Stop; no retry; record and surface |
| Budget exhausted | Stop safely; keep state; ask for more or for manual continuation |
| Worker crash | Resume from the checkpoint under a new fenced attempt |

**Leases and fencing.** Workers claim work with a lease and a fencing token, so a late, obsolete attempt can never commit over accepted work.

**Cancellation** is a state (`CANCELLING`), not a flag. It fences workers and children, stops new effects, reconciles effects already in flight, and records what was and was not undone. Rolling back code never undoes an external effect; compensations are recorded.

### Approvals, trust and tenancy

- **Approval binding.** An approval records the approver, the exact action and arguments, the artifact version and content hash, the policy revision, any conditions and an expiry. Any material change invalidates it and needs re-approval. Revocation is modelled.
- **Untrusted content stays out of the authority path.** Text from tools, pages, files or models can never grant a permission, change a policy or trigger a protected action. Injection attempts are detected, contained and logged.
- **Tenant isolation end to end:** the tenant ID flows through database filters or row-level security, caches, retrieval, artifacts, queues, credentials, logs and model routing.

### Models, prompts and skills

- **Capability, not model name.** Tasks declare what they need (reasoning, structured output, vision, long context); a router chooses the model under privacy, region, budget and quality rules.
- **Every inference records** the model, generation settings, prompt and skill versions, schema validation result, tokens and cost.
- **Prompts and skills are versioned releases** with tests and evals. A skill manifest declares its tasks, inputs, outputs, tools, permissions and success criteria; a skill never grants authority.
- **Fallback** happens only on named failures, revalidates the output, respects cost limits and records the model actually used.

**Budgets.** Budget is reserved at admission, before dispatch, including retries and children, and enforced by tenant, project and provider under parallelism. When a budget runs out mid-loop, the run stops, keeps a safe incomplete state and says what would unblock it.

### AG-UI: the contract between agents and the UI

AG-UI (Agent–User Interaction protocol) is how our agents stream to the frontend. It is the interaction plane's event contract, one of three protocol layers:

| Layer | Protocol | Connects |
| --- | --- | --- |
| Agent ↔ user | AG-UI | Run lifecycle, steps, messages, tool activity, state and approvals, streamed to the app |
| Agent ↔ tools and data | MCP | Tools, data and services an agent may call, behind the tool gateway |
| Agent ↔ agent | A2A | Delegation to agents in other systems |

**How it works.** A run produces a stream of typed JSON events, over Server-Sent Events by default. A run can be started by an AG-UI run request (thread, run, messages, shared state, frontend tools, context) or by a normal API command whose run the UI then observes; the ADR picks one per product. The canonical `ExecutionEvent`s are projected into AG-UI events, never the other way round.

| Event family | Events | Projected from | What the UI does |
| --- | --- | --- | --- |
| Lifecycle | `RUN_STARTED`, `RUN_FINISHED`, `RUN_ERROR`, `STEP_STARTED`, `STEP_FINISHED` | Run and task state changes | Run indicator with the current step; end and typed error states |
| Text | `TEXT_MESSAGE_START`, `_CONTENT`, `_END` | Agent replies (chat products only) | Streams the reply |
| Tool calls | `TOOL_CALL_START`, `_ARGS`, `_END`, `_RESULT` | `ToolRequested`, `ToolAuthorized`, `ToolCompleted` | Shows what the agent is doing; renders typed generative UI and approval requests |
| State | `STATE_SNAPSHOT`, `STATE_DELTA` (JSON Patch), `MESSAGES_SNAPSHOT` | Read-model projections | Keeps drafts, progress and waiting reasons in sync |
| Activity | `ACTIVITY_SNAPSHOT`, `ACTIVITY_DELTA` | Long-running work, pauses, waits | Progress, and why a run is blocked or waiting |
| Special | `RAW`, `CUSTOM` | Product events | Product-specific updates, namespaced |

The protocol is still adding events (reasoning and sub-agent events are in the draft), so each product pins its AG-UI SDK versions in `TECH_STACK.md` and upgrades them through a spec.

**Rules for AG-UI in our products:**

- **Commands, observations and state are separate.** The UI sends commands to the API, subscribes to events, and renders authoritative state. A UI command is never authoritative until the server validates it; events never carry authority.
- **The UI reads state from events and snapshots, never from text.** Forms, cards, progress and blocked reasons come from typed events.
- **Reliable resume.** Every event carries a per-stream sequence used as the resume cursor. On reconnect the server sends a snapshot and then the events after the cursor; the client checks sequence and drops duplicates. Nothing is ever replayed as an action.
- **Human in the loop.** An approval request is shown from a typed event. The decision goes back as an authenticated command bound to the exact version (see approval binding). Pause, cancel, edit, approve, reject, re-plan and resume each have explicit server semantics.
- **Typed generative UI.** An agent may only ask for components and actions from an approved registry with schemas. It never sends executable HTML or JavaScript.
- **Redacted.** Events carry summaries and references, never secrets, signed URLs, raw prompts or untrusted page text. Payloads are fetched through authorised APIs.
- **Scoped and renewed.** The stream is authorised per tenant and resource like every route, and renews or closes when the user's token expires.
- **Legible.** The UI can always say what a run is doing, why it is blocked or waiting, which task caused it and what evidence exists.
- **Errors are typed.** `RUN_ERROR` carries the product's error class, so the UI shows the right repair action.
- **A versioned contract.** The SDK versions, the event mapping, custom events (`<product>.<name>`), shared state schemas and any frontend tools live in `docs/contracts/agui/`. Recorded streams are replayed in tests.

### Assurance

| Suite | Minimum coverage |
| --- | --- |
| Unit and contract | State machine guards, schema versions, tool authorisation, event projection, budget arithmetic |
| Integration | Database and outbox, sandbox, model adapter, approval service, external adapters |
| End-to-end | One real, safe vertical slice per product journey |
| Adversarial | Prompt injection, tenant crossover, malicious tool output, delegated privilege escalation |
| Fault and chaos | Worker death, delayed results, duplicate events, lost receipts, network partition, stale context |
| Behavioural eval | Goal fulfilment, tool correctness, grounding, boundedness, abstention |
| Release assurance | Independent checks on the exact build; a policy change needs re-approval |
| Operations | Queue delay, recovery time, cost per run, agent steps, tool failure rate, incident drills |

- Thresholds are set per product in `TEST_STRATEGY.md` or an ADR, never as invented universal numbers.
- Hard gates use deterministic checks; a model judge never replaces them.
- Eval datasets are versioned, holdout data is kept apart, and counterexamples are kept as evidence.
- A verifier is independent: an agent that writes or repairs something can never edit the criteria that judge it.

**Conformance scenarios.** Every agentic product plans these as `T-xx` in Stage 3 (those that cannot apply are marked "not applicable" with the reason):

| ID | Fault or attack | Expected result |
| --- | --- | --- |
| C01 | Duplicate transition command | One transition; replay-safe receipt |
| C02 | Tool call outside the allowed capability | Denied before any effect; decision logged |
| C03 | Two dependencies complete at once | The dependent task is dispatched once |
| C04 | Worker dies after an external write | Receipt reconciled before any retry |
| C05 | Approval bound to an old version | Approval invalid; promotion blocked |
| C06 | Tool output contains malicious instructions | Treated as data; exfiltration denied |
| C07 | Cross-tenant memory, cache or retrieval lookup | Rejected and audited |
| C08 | Sub-agent asks for more privilege or budget | Denied; budget unchanged |
| C09 | User edits an input during inference | Stale result rejected or revalidated |
| C10 | Stream reconnects after lost events | Snapshot plus cursor converge to current state |
| C11 | Budget exhausted mid-loop | Stops; safe incomplete state kept |
| C12 | Old workflow resumes after a deploy | Pinned version honoured, or a documented migration |
| C13 | A repair agent changes trusted tests | Write denied; release blocked |
| C14 | Verified build differs from the deployed one | Blocked until the exact artifact is re-verified |

### Agent decisions to record

Before agent implementation starts (by the end of M0), each topic below has an ADR, or a link to the ADR that already covers it, with the owner, options, rationale, test scenario and rollback:

1. authoritative state and transaction boundaries;
2. harness interface and checkpoint semantics;
3. task and event schemas and version compatibility;
4. sandbox isolation and tool authorisation;
5. scheduler, leases, fencing and reconciliation;
6. context freshness, retrieval permissions and memory writes;
7. model routing, budgets, fallback and data residency;
8. artifacts, identity, provenance and trusted verification;
9. the streamed UI (AG-UI) and approval binding;
10. operational security, retention, SLOs and disaster recovery.

### Anti-patterns

| Anti-pattern | Replace with |
| --- | --- |
| The agent decides whether it is authorised; policy lives in the prompt | Control-plane guards and gateway checks in code |
| A chat-wrapped form presented as L4 | Maturity claimed per workflow, from tested behaviour |
| Claiming success before the system of record confirms | Report only reconciled outcomes |
| Silent derivation: an inferred value treated as fact | Show sources; confirm uncertain or high-impact values |
| Overasking for verified information | Reuse authorised context; ask only for what is missing |
| One shared, mutable, global agent memory | Scoped, versioned context and immutable artifacts |
| A DAG used for an unbounded conversation | A nested loop sub-workflow with termination |
| Model output directly changes a protected status | A structured proposal plus deterministic verification |
| Blind retry after a remote timeout | Receipt lookup, idempotency, reconciliation |
| A frontend that only consumes a token stream | Typed event projection plus authoritative snapshots |
| A tool adapter holding a long-lived credential | Short-lived, scoped capabilities |
| Framework-specific state as product state | Neutral, versioned contracts and events |
| "All green" from the agent's own test report | A trusted verifier reproduces the result on the exact build |
| Proactive noise: counting alerts, not useful interventions | Throttled, deduplicated, measured interventions |
| Judging an agent by a polished demo | Backend correctness and outcome metrics |

### Where agent architecture shows up in the process

| Stage | What it adds |
| --- | --- |
| 1 Intake | Each journey step an agent performs, its target maturity level, and the human decision it prepares, in the stories |
| 2 Design | `AGENT_ARCHITECTURE.md`; ADRs for the ten decisions above; contracts for task contracts, results, events and AG-UI; agent threats in `SECURITY.md`; agent telemetry in `OBSERVABILITY.md`; agent surfaces (run status, approval requests, blocked reasons) on the design canvas |
| 3 Plan | One spec per agent task; conformance scenarios and eval thresholds in `TEST_STRATEGY.md`; `.cursor/rules/agent.mdc` |
| M0 | Harness interface with a fake model and fake tools, tool gateway, outbox and the event stream; C01–C04 passing |
| 4–5 Build and verify | One real vertical slice per journey; C05–C11 before the first feature milestone exits; C12–C14 and restore drills before go-live |
| 6–7 Release and learn | Prompts, models, skills and policies released with their evals; maturity reviewed per workflow at each retro |

**Agent review checklist (part of G2 for agentic products):**

- run, task, attempt and artifact owners are named, and the lifecycle and its guards are documented;
- every privileged action has an authorisation check and an approval binding;
- the four schemas are versioned and the tool gateway denies forbidden calls independently of prompts;
- every external write is idempotent or reconciled;
- the UI can rebuild run state after a reconnect, and an operator can explain every blocked or waiting state from stored evidence;
- the maturity level of each workflow is recorded with its exit evidence.

## Stage 3 — Plan

Planning turns the design into three things: an ordered spec backlog, a test strategy with CI/CD gates, and a milestone schedule the client agrees to. The development plan is the engineering view; the delivery plan is the client view.

| Doc | Audience | Contents |
| --- | --- | --- |
| `DEVELOPMENT_PLAN.md` | Engineers | Features split into specs `SPEC-xx`, each one PR of about 1–3 days; dependency order, the screens S-xx each frontend spec builds, and which specs run in parallel; branch naming, coding standards, the Cursor and Claude workflow |
| `TEST_STRATEGY.md` | Engineers, QA | Test levels and owners; what runs per PR, nightly and per milestone; eval suites, thresholds and test data; the agent conformance scenarios C01–C14 as `T-xx`; Definition of Done; CI/CD pipeline and environments |
| `DELIVERY_PLAN.md` | Client, product | Milestones M0–Mn with the `R-xx` each delivers; dates, demo and UAT slots; risks, assumptions, issues and dependencies (RAID) |

**Agent rules.** Stage 3 also writes the instructions every Cursor run follows. They are derived from `TECH_STACK.md`, `ARCHITECTURE.md`, the ADRs and the development plan, and committed in M0. Write each rule as an `.mdc` file with frontmatter (`description`, `globs`, `alwaysApply`) so it loads only where it applies, and keep shared, unscoped instructions in `AGENTS.md` ([Cursor docs](https://cursor.com/docs/rules)).

| File | Applies when | Holds |
| --- | --- | --- |
| `AGENTS.md` (repo root) | Every agent run | Product summary, repo map, the make targets (setup, up, test, lint, check), where specs and contracts live, global don'ts |
| `.cursor/rules/000-core.mdc` | Always (`alwaysApply: true`) | Coding standards, ID conventions, branch and commit rules, "never change a contract outside a spec" |
| `.cursor/rules/backend.mdc` | `globs: backend/**` | Layering, error handling, database and migration rules, test style |
| `.cursor/rules/frontend.mdc` | `globs: web/**` | Component and state patterns; screens in docs/design/screens/ are the visual reference, rebuilt with the app's components and tokens, never copied; accessibility, languages, test style |
| `.cursor/rules/agent.mdc` | `globs: agent/**` | The golden rules and the execution contract, harness interface, tool gateway order, the three validation stages, AG-UI rules, prompt and tool conventions, model mocking, eval scenario format |
| `.cursor/rules/testing.mdc` | `globs: **/tests/**` | Test levels, fixtures, `T-xx` naming |
| `.cursor/rules/observability.mdc` | Code that adds a flow | Span, log and metric conventions |
| `CLAUDE.md` | Claude PR review | Review checklist; points to `AGENTS.md` so both tools share the same conventions |

Each rule states the decision and links its ADR for the reason. Keep each under 500 lines. When Cursor or the review repeats a mistake, fix the rule in the same PR.

**Gate G3:**

- every Must `R-xx` is in a milestone;
- every spec lists its `R-xx` and `T-xx`, and every frontend spec its approved `S-xx`;
- the client agrees what is in each milestone and when.

## Milestones

Every product starts with M0, a walking skeleton that proves the pipeline end to end. Feature milestones follow, each a demoable vertical slice of PRD features. A hardening milestone closes the project.

| Milestone | Delivers | Exit criterion |
| --- | --- | --- |
| M0 Foundation | Repo, Makefile and Docker Compose stack, CI/CD, dev and staging environments, auth skeleton, database and migrations, observability wiring, contract stubs, AGENTS.md and Cursor rules, test harnesses (unit, integration, Playwright, agent mock and eval runner); for agentic products, the harness interface with fake model and tools, the tool gateway, the outbox and the AG-UI stream | One trivial request goes frontend → backend → agent → database, traced, and is deployed by the pipeline; a fresh clone runs with make setup and make up; agent conformance C01–C04 pass |
| M1–Mn Features | The specs for a set of features, usable end to end by a real user role | Milestone exit checklist below |
| Hardening | Performance, security and accessibility testing, runbook, handover | NFRs verified, runbook rehearsed, go-live checklist signed |

**Milestone exit checklist (G4):**

- all milestone specs merged and marked Done in `STATUS.md`;
- the E2E Playwright suite is green on staging, and the built screens match their approved S-xx, states included;
- the agent eval suite meets its thresholds over N runs, and the milestone's conformance scenarios pass;
- no open Severity 1 or 2 bugs;
- dashboards and alerts exist for the new flows;
- the client accepts the demo or UAT;
- release notes, `CHANGELOG.md` and a version tag are done;
- the retro is held and its actions recorded.

**Bug severity.** Bugs are tracked as issues linked to their `R-xx` and `SPEC-xx`:

- Sev 1: production down, data loss or a security breach. Fix immediately.
- Sev 2: a Must requirement broken with no workaround. Fix before milestone exit.
- Sev 3: broken, but a workaround exists. Schedule it.
- Sev 4: cosmetic. Fix when convenient.

## Build loop for each spec

Every spec goes through the same eight steps. Nothing reaches `main` without green CI, an AI review and a human approval.

&#91;embedded content: spec build loop · 6 steps, 2 checks\]

A red CI run, an unresolved review comment or a change request each send the spec back to Cursor on the same branch.

1. **Ready.** The spec meets the Definition of Ready:
   - `R-xx` linked and acceptance criteria written;
   - contract references, approved screens S-xx (for frontend specs) and test plan (`T-xx`) present;
   - dependencies merged;
   - the expected diff is under about 400 changed lines. A larger spec is split.
2. **Branch.** Create `feat/SPEC-xx-short-name` from the latest `main`, or `fix/`, `chore/` or `docs/` for other work. Merge it within about 1–3 days.
3. **Prompt.** Write the Cursor prompt from the template and save it at `plans/Mx/specs/SPEC-xx/prompt.md`, so the run can be repeated and reviewed.
4. **Implement.** Cursor (Composer 2.5) writes the code and the tests together, guided by AGENTS.md and the Cursor rules. The engineer reads the diff, runs the tests locally and iterates.
5. **Pull request.** Use a Conventional Commit title and fill the PR template with the spec, requirement, screen and test IDs.
6. **CI.** All required checks must pass (see CI/CD).
7. **Review.** Claude checks correctness against the spec and its screens, security and test gaps, and posts PR comments. The author resolves them, and a human reviewer or code owner approves.
8. **Merge.** Squash-merge to `main`; it deploys to dev automatically. Update the spec row in `STATUS.md` and delete the branch. When every spec for a screen has merged, mark the screen Built.

**Definition of Done for a spec:**

- acceptance criteria are covered by passing tests;
- make check passes locally, CI is green and the review is approved;
- contracts, ADRs and docs are updated where touched;
- new code paths emit traces and logs, and the rules are updated if a convention changed;
- `STATUS.md` is updated.

**AI tool hygiene.** Confirm at intake that the client allows AI-assisted development and which tools. Never put secrets, credentials or real client data into prompts, screens or fixtures; use synthetic data. Turn on Cursor's privacy mode where the client requires it.

## Testing model

Tests follow the pyramid: many fast tests on every PR, fewer cross-component tests nightly, and the full E2E and eval suites at each milestone. The tools listed are examples; pick yours in `TECH_STACK.md`.

| Level | Scope | Example tools | Runs | Gate |
| --- | --- | --- | --- | --- |
| Backend unit | Functions and services in isolation | pytest | Every PR | Must pass; coverage floor on changed code |
| Backend functional | API endpoints against a real database in a container | pytest, httpx, Testcontainers | Every PR | Must pass |
| Frontend unit and component | Components, hooks, state | Vitest, Testing Library | Every PR | Must pass |
| Contract | Backend ↔ frontend, backend ↔ agent task and tool schemas, and the AG-UI contract | OpenAPI and JSON Schema validation, Pact | Every PR | No breaking change without a version bump |
| Integration (BE + FE) | Real backend and frontend with seeded data; screenshot checks of key screens against their S-xx | Playwright | Smoke on every PR, full suite nightly | Must pass |
| Agent, mocked | Agent logic with a stubbed model and recorded responses | pytest, fixtures | Every PR | Deterministic; must pass |
| Agent conformance | C01–C14 faults and attacks (see Agent architecture) with fake models and tools | pytest, Testcontainers, Playwright | Every PR for C01–C04, nightly for the rest | Must pass |
| Agent, live eval | Real model over a scenario set, N ≥ 10 runs | Eval runner | Nightly and per milestone | Pass rate at or above threshold; zero safety failures |
| E2E (BE + FE + agent) | Full user journeys including the agent | Playwright and the eval suite | Per milestone on staging, and nightly | Milestone exit gate |
| Non-functional | Load, security scanning, accessibility | k6, OWASP ZAP, axe | Hardening, and per milestone for key flows | NFR targets met |

Agent evals need their own discipline:

- versioned scenario sets with expected outcomes;
- graders that are rule-based where possible, with model-graded checks only where needed;
- tracked metrics: task success, tool-call correctness, grounding, abstention, policy denials, state transitions, retries, safety violations, latency, cost;
- a red-team set for prompt injection, malicious tool output and privilege escalation;
- deterministic checks for every hard gate; a model judge never replaces them;
- an independent verifier: the agent under test can never edit its criteria;
- recorded AG-UI streams replayed against the UI in Playwright;
- any regression against the last milestone blocks exit.

## CI/CD pipeline

One pipeline promotes the same build artifact from PR to dev, staging and production, with a gate at each step.

**Make and Docker.** Every task runs through one `Makefile`, and every service runs in a container through Docker Compose. Engineers, CI and Cursor use the same commands, so a green local run predicts a green PR.

| Target | Does |
| --- | --- |
| `make setup` | First-time setup: copy `.env.example` to `.env`, build the images, install git hooks |
| `make up`, `make down` | Start or stop the full local stack (services, database, any queues) |
| `make migrate`, `make seed` | Apply database migrations; load the synthetic fixtures |
| `make lint`, `make fmt` | Lint, type-check and format every service |
| `make test` | Unit, functional and component tests |
| `make test-int`, `make test-e2e` | Playwright integration and E2E runs against the running stack |
| `make eval` | Agent eval suite: mocked by default, live model with `LIVE=1` |
| `make check` | Everything the PR checks run; must pass before a PR is opened |

- CI jobs call these same targets rather than their own scripts.
- The host needs only Docker, make and git; no language toolchains installed locally.
- The same Dockerfiles build the images deployed to dev, staging and production.
- Secrets come from a git-ignored `.env` locally and from the vault elsewhere; `.env.example` is committed.

| Stage | Trigger | Checks | Blocks |
| --- | --- | --- | --- |
| PR checks | Every push to a PR | Lint, format, type check; every-PR tests from the testing model, including the Playwright smoke run; build and migration check; static analysis, dependency scan, secret scan | Merge |
| Main | Merge to `main` | Build the image, deploy to dev, smoke test | — |
| Nightly | Schedule | Full Playwright suite, live agent eval, dependency audit | Milestone sign-off while red |
| Release candidate | `vX.Y.0-rc` tag | Deploy to staging, E2E and eval suites, performance checks | Production promotion |
| Production | Approved release tag | Deploy behind feature flags, run migrations, smoke test, keep rollback ready | — |

**Practices:**

- branch protection on `main` through a ruleset: pull request required, squash merge only, linear history, conversations resolved, no force pushes or deletions, and the required checks once CI exists. Require at least one approval; a solo owner sets zero approvals and adds the repository admin to the bypass list "for pull requests only", so direct pushes stay blocked. Private repos need GitHub Pro or Team for rulesets to be enforced;
- GitHub flow with short-lived branches;
- feature flags for work that is merged but not yet released;
- SemVer tags and a `CHANGELOG.md` generated from Conventional Commits;
- infrastructure as code, and secrets in a vault, never in the repo;
- automated dependency updates (Renovate or Dependabot) and a licence check, each update merged through a normal PR;
- DORA metrics (deploy frequency, lead time, change failure rate, time to restore) reviewed at each retro.

## Observability

Observability is built in M0 and extended by every spec, so each new flow ships with its traces, logs, metrics and alerts.

- **Traces.** OpenTelemetry spans run across frontend → backend → agent → database, with one trace ID per user request.
- **Logs.** Structured JSON carrying the trace ID, request ID and tenant or user ID, with PII redacted.
- **Metrics.** Rate, errors and duration for every endpoint and job.
- **Agent telemetry.** Each run records:
  - model calls and tool calls;
  - tokens and cost;
  - latency;
  - model and prompt versions;
  - budget reserved and settled, retries and their failure class;
  - every authorisation decision and approval wait.

  An operator can explain every blocked or waiting run from these records.

  Eval scores are kept over time.
- **SLOs.** Availability and latency targets per key journey, with alerts on error-budget burn rather than raw thresholds.
- **Per-spec rule.** A spec that adds a flow also adds its spans, log events and dashboard panel. This is part of the Definition of Done.

## Operate and support

Go-live starts the operate phase. It needs its own plan, written into `RUNBOOK.md` during hardening.

- **Hypercare.** A fixed period after go-live (often two to four weeks) with daily checks of errors, SLOs and agent evals, and fast fixes.
- **On-call and escalation.** Who responds, how they are reached, and the response time for each bug severity.
- **Agent controls.** Kill switches per agent task and per tool, credential revocation, and an audit export, rehearsed in hardening.
- **Incidents.** Each Sev 1 or Sev 2 incident gets a blameless postmortem in `docs/ops/incidents/` within a week, and its actions become specs or rules.
- **Backups and recovery.** Recovery point and recovery time targets come from the NFRs. A restore is rehearsed in hardening and on a schedule after that.
- **KPI review.** About 30 days after each release, compare the `KPI-xx` targets with the analytics, and feed the result into the retro and the next change requests.
- **Handover.** If another team will run the product, hand over the runbook, dashboards, access and a walkthrough before G5.

## Tracking and change control

`STATUS.md` is the one place to check progress. Every change to the PRD goes back through intake before it reaches the plan.

**`STATUS.md` holds:**

- the current milestone and next gate;
- the milestone table;
- the spec table for the current milestone, with each spec's screens, branch and PR, and the screen table (each S-xx with its requirements, specs and status);
- open questions and risks;
- recent ADRs.

Specs move through Draft → Ready → In progress → In review → Done, or Blocked with a reason. Screens move through Draft → Client review → Approved → Built.

Each week, send the client a short update generated from `STATUS.md`: what was done, what is next, risks, and decisions needed from them.

**Change control:**

1. Store the new PRD version or change request unchanged, as `CR-xx`.
2. Diff it against `REQUIREMENTS.md` and list the affected requirements, screens, ADRs, contracts, specs, tests and milestone dates.
3. The client approves the scope and date impact.
4. Update the owning docs downstream, add or change specs, and update `STATUS.md`.

No spec work starts on an unapproved change.

**Frozen and living docs:**

- `REQUIREMENTS.md`, `ARCHITECTURE.md`, `AGENT_ARCHITECTURE.md`, `UI_DESIGN.md` and the approved screens are baselined at their gates and change only through change control.
- `STATUS.md`, ADRs, specs and the development plan are living docs.

## Repo layout

Every product repo uses the same layout, so the docs are always in the same place.

```
AGENTS.md         instructions every coding agent reads
CLAUDE.md         Claude review checklist, points to AGENTS.md
.cursor/rules/    000-core.mdc, backend.mdc, frontend.mdc, agent.mdc, ...
docs/
  PROCESS.md      this process, exported as Markdown
  sources/        PRD and client inputs, versioned; revised only by the product owner
  product/        REQUIREMENTS.md, QUESTIONS.md, UI_DESIGN.md
  design/         tokens.md, screens/S-01-<name>.html, ...
  discovery/      DISCOVERY.md (only if an existing system is involved)
  architecture/   ARCHITECTURE.md, AGENT_ARCHITECTURE.md, TECH_STACK.md, SECURITY.md, OBSERVABILITY.md
  adr/            ADR-001-<slug>.md, ...
  contracts/      openapi.yaml, events/, agent-tools/, agui/
  ops/            RUNBOOK.md, RELEASE_NOTES.md, incidents/
plans/
  STATUS.md
  DEVELOPMENT_PLAN.md
  TEST_STRATEGY.md
  DELIVERY_PLAN.md
  M0/, M1/, ...   milestone.md and specs/SPEC-xx/{spec.md, prompt.md}
  retros/         M0.md, M1.md, ...
.github/          workflows/, pull_request_template.md, CODEOWNERS
Makefile          setup, up, down, test, lint, eval, check, ...
compose.yaml      local stack: every service plus database
docker/           one Dockerfile per service
.env.example      config keys with safe defaults; .env stays untracked
CHANGELOG.md
```

## Templates

Copy these into each new repo. The spec and the prompt are the two that matter most, because they drive every Cursor run.

**Spec** (`plans/Mx/specs/SPEC-xx/spec.md`)

```markdown
# SPEC-xx: <title>
Milestone: Mx | Status: Draft | Layer: backend / frontend / agent / cross-cutting
Agent (if any): task contract, maturity level, conformance scenarios C-xx
Requirements: R-xx, R-yy | Feature: F-xx | ADRs: ADR-xxx
Screens: S-xx (docs/design/screens/S-xx-<name>.html) | Branch: feat/SPEC-xx-<name>

## Goal
One sentence: what a user can do once this merges.

## Scope
In: ...
Out: ...

## Design
Components touched, contract references, data changes, migrations.

## Acceptance criteria
- AC1: Given ... when ... then ...

## Tests
- T-xx unit: ...
- T-xx functional / integration: ...
- T-xx E2E or eval scenario: ...

## Observability
Spans, log events and metrics added.

## Dependencies
Specs that must merge first; contract versions.
```

**Cursor prompt** (`plans/Mx/specs/SPEC-xx/prompt.md`)

```markdown
Model: Composer 2.5 | Branch: feat/SPEC-xx-<name>

Context: read plans/Mx/specs/SPEC-xx/spec.md, docs/contracts/<file>,
docs/adr/ADR-xxx.md, docs/design/screens/<S-xx file>,
docs/design/tokens.md and <relevant folders>.
Task: implement SPEC-xx exactly as specified.
Boundaries: change only <paths>; do not change public contracts.
Screens: match the screen's layout, copy and empty / loading / error states.
Rebuild it with the app's components and tokens; never copy its HTML.
Tests: write the tests under "Tests" first, make them pass, run make check.
Rules: AGENTS.md and .cursor/rules apply; flag any new dependency; no secrets in code.
Report: changes made, tests added, any deviation from the spec and why.
```

**ADR** (`docs/adr/ADR-xxx-<slug>.md`)

```markdown
# ADR-xxx: <decision>
Status: Proposed | Accepted | Superseded by ADR-yyy    Date: YYYY-MM-DD
Context: the forces and the R-xx / NFR-xx behind this choice.
Decision: what we chose.
Alternatives: what we considered and why we rejected each.
Consequences: what gets easier, what gets harder, what we must now do.
```

**Pull request** (`.github/pull_request_template.md`)

```markdown
## SPEC-xx: <title>
Requirements: R-xx | Screens: S-xx | Tests: T-xx
### What changed
### How it was tested
### Screenshots or traces
### Risk and rollback
- [ ] Acceptance criteria met
- [ ] Tests added or updated
- [ ] Contracts and docs updated
- [ ] STATUS.md updated
```

**Status** (`plans/STATUS.md`)

```markdown
# STATUS: <product>        Updated: YYYY-MM-DD
Current milestone: Mx | Next gate: <gate> on YYYY-MM-DD

| Milestone | Scope | Status | Exit date |
|---|---|---|---|

## Mx specs
| Spec | Requirements | Screens | Branch / PR | Status | Owner |
|---|---|---|---|---|---|

## Screens
| Screen | Requirements | Specs | Status |
|---|---|---|---|

## Open questions and risks
## Recent decisions
```

## What changed from the draft, and standards alignment

The draft's core shape is kept: PRD → design → plans → milestones of specs → branch, Cursor, PR, CI and Claude review → `STATUS.md`. The changes below close the gaps an industry-standard process would flag.

| Draft | Polished | Why |
| --- | --- | --- |
| PRD goes straight to architecture | Requirements intake and gate G1 come first | A client PRD has gaps. Catching them before design is cheapest, and it creates the IDs used for tracing |
| Decisions as a step after architecture | ADRs written during design | Decisions are made while designing; recording them later loses the reasons |
| One architecture and implementation plan | `ARCHITECTURE.md` (design) plus `DEVELOPMENT_PLAN.md` (specs and tasks) | Design changes slowly; the task plan changes weekly |
| Tech stack as its own step | Tool choices made as ADRs, summarised in `TECH_STACK.md` | Every tool keeps its reason |
| No contracts step | API, event and agent-tool schemas before work splits | Enables parallel work and contract tests |
| No security step | `SECURITY.md` threat model plus scans in CI | A baseline expectation, and more important with agents |
| Agents treated as a feature | An agent architecture: maturity per workflow, planes, execution contract, AG-UI and conformance scenarios | Agent authority, recovery and approvals must be designed, not prompted |
| Observability as a layer | Built in M0, extended by every spec | Adding tracing later is expensive |
| Ad hoc Cursor prompts | One saved prompt per spec, plus versioned AGENTS.md and Cursor rules | AI work becomes repeatable and reviewable, and conventions hold on every run |
| CI and Claude approve the merge | CI, then Claude review, then a human approval | A person stays accountable; AI review assists |
| Tests per layer | Plus when each runs (PR, nightly, milestone) and its threshold | Keeps PR checks fast and evals meaningful |
| `STATUS.md` only | Plus change control, milestone exit checklist and retros | Clients change scope, so the process needs a loop |

| Practice | Standard or reference |
| --- | --- |
| Lifecycle stages | ISO/IEC/IEEE 12207 |
| Requirements quality; NFR categories | ISO/IEC/IEEE 29148; ISO/IEC 25010 |
| Architecture description | C4 model, arc42, ISO/IEC/IEEE 42010 |
| Decision records | ADRs (Michael Nygard format) |
| Secure development | NIST SSDF (SP 800-218), OWASP ASVS, OWASP Top 10 for LLM Applications |
| AI risk | NIST AI Risk Management Framework |
| Agent architecture and maturity | Agentic Application Reference Architecture v1.2, Engineering Practices Guidebook v1.0, Agent Capability Maturity Framework (internal) |
| Agent interfaces | AG-UI (agent ↔ user), Model Context Protocol (agent ↔ tools), A2A (agent ↔ agent) |
| Branching, commits, versions | GitHub flow, Conventional Commits, Semantic Versioning |
| Delivery performance | DORA metrics |
| Observability | OpenTelemetry; SLOs and error budgets (Google SRE) |
| Ready and Done | Definition of Ready and Definition of Done (Scrum) |

## Running it in a Claude project

Set up once per product, then run one stage per thread. Generated docs live in the Git repo. The project holds only this process and the PRD.

**One-time setup**

1. Create an empty private GitHub repo for the product, set "Automatically delete head branches" and squash-only merging, and add the `main` ruleset (see CI/CD practices). Add required checks after M0 delivers CI.
2. In Claude, connect GitHub and install the Claude GitHub App on that repo, so threads can push branches and open PRs.
3. Export this doc as Markdown and name it `PROCESS.md`.
4. Create a Claude project. Attach the repo with push access, and upload `PROCESS.md` and the PRD as project files.
5. Paste the project instructions below, with the placeholders filled in.
6. Run the stage prompts below in order, each in a new thread. Review and merge each PR before starting the next stage.

If a thread cannot push, ask it for the files instead and commit them yourself.

**Project instructions** (paste into the project's custom instructions)

```text
Project: <Product name>. <One-sentence summary of what it does and for whom>.
Built from the client PRD using the process in PROCESS.md.

Where things are
- Process: PROCESS.md (project file). It defines the stages, gates, docs,
  IDs and templates. Follow it.
- PRD: <PRD file name> (project file), copied into docs/sources/. Edit it only
  when I say so, with a dated revision note, in both places.
- Repo: github.com/<owner>/<repo> (attached). The repo is the source of truth
  for every generated doc. Start every session from plans/STATUS.md.

Rules
- One stage per thread. Do only the stage asked for, stop at its gate,
  and list what I need to review or decide.
- Use the IDs from PROCESS.md (R-xx, NFR-xx, KPI-xx, F-xx, Q-xx, A-xx, ADR-xxx,
  S-xx, SPEC-xx, T-xx). Every requirement traces to a PRD section.
- Never invent requirements. A gap becomes a Q-xx with an assumption A-xx.
- One owner per fact: link to the owning doc instead of repeating it.
- Work on a branch named in the stage prompt and open a PR. Never push to main.
- Update plans/STATUS.md at the end of every stage.
- Ask me before choices that are expensive to reverse (cloud, database,
  model provider, auth). Decide the rest, record an ADR, and say which.

Stack: <known constraints, or "decided in stage 2">.

How I like to work: short replies, lead with the answer. When I say
"your call", pick a sensible default, say which, and continue.
```

**Stage prompts** (one thread each; replace the `<...>` parts)

**0. Bootstrap the repo**

```text
Set up the repo per the "Repo layout" in PROCESS.md. Copy the PRD into
docs/sources/ unchanged as PRD-v1.0.<ext>, and PROCESS.md into docs/.
Create every folder and doc as a stub with headings only. Create
plans/STATUS.md from the Status template (current: Stage 1, next gate: G1),
the PR template and CHANGELOG.md. Leave AGENTS.md and the Cursor rules for
Stage 3. Branch chore/bootstrap, open a PR, and summarise.
```

**1. Requirements intake**

```text
Run Stage 1 on docs/sources/<PRD file>.
- Product framing: confirm the PRD's personas, user journeys, user stories,
  and value and defensibility hypotheses; for agentic products, the agent
  steps per journey with their target maturity level; propose any that are
  missing in REQUIREMENTS.md and raise a Q-xx for each.
- docs/product/REQUIREMENTS.md: R-xx and NFR-xx, each with its PRD section,
  MoSCoW priority and Given/When/Then acceptance criteria; grouped into F-xx;
  an out-of-scope list; a coverage table (every PRD section -> R-xx or out
  of scope).
- docs/product/QUESTIONS.md: Q-xx, each with the assumption A-xx you would
  build on.
- DISCOVERY.md only if the PRD depends on an existing system.
Check Gate G1 and list what fails. Give me the open questions grouped by who
must answer them. Branch docs/stage-1-intake, PR, update STATUS.md.
```

After the client answers, in the same thread:

```text
Answers: <Q-xx: answer, ...>. Update REQUIREMENTS.md and QUESTIONS.md, mark
the questions resolved, and re-check G1.
```

**2. Design** (for a large PRD, split into 2a: architecture, ADRs and contracts; 2b: the rest)

```text
Run Stage 2 from docs/product/REQUIREMENTS.md, in the order PROCESS.md gives:
ARCHITECTURE.md (C4 levels 1-3 as Mermaid, data model, write path, a quality
scenario per NFR, an R-xx -> component table); for agentic products,
AGENT_ARCHITECTURE.md per the Agent architecture section (maturity per
workflow, planes, journeys -> agents, execution contract, AG-UI, conformance
scenarios); an ADR for each significant
choice, written as you make it; docs/contracts/ (OpenAPI, event schemas,
agent task, result and tool schemas, the AG-UI contract); UI_DESIGN.md (journeys and stories in scope, screens,
flows, states, an R-xx -> screen table); TECH_STACK.md (each tool linked to its ADR); SECURITY.md (STRIDE,
roles, data classification, agent risks); OBSERVABILITY.md (signals, SLO per
key journey). Check Gate G2 (screen approval comes in 2c) and list the gaps. Branch docs/stage-2-design,
PR, update STATUS.md.
```

**2c. Screens**

```text
Run the Screens step of Stage 2 from docs/product/UI_DESIGN.md. Put the shared
colours, type and spacing in docs/design/tokens.md. In Claude Design, make one
canvas: a journeys -> stories -> screens map, a "what it solves" page
(problems -> screens -> KPI-xx, moat hypotheses), and one page per journey
with its screens in step order, linked for click-through, each with a note
naming its journey step, stories, gate, R-xx, problem solved, moat built and
states to come. Give each screen an ID S-xx. Link the canvas from STATUS.md,
set the screens to Client review, and stop for my review on the canvas.
Branch design/screens-v1, PR.
```

After client feedback, in the same thread:

```text
Feedback: <S-xx: change, ...>. Update those screens on the canvas, and set the
approved ones to Approved in STATUS.md. Re-check Gate G2.
```

Once the canvas is approved, in the same thread:

```text
Build each approved screen as a self-contained HTML prototype matching the
canvas, with realistic synthetic data and its empty, loading and error states,
in docs/design/screens/S-xx-<name>.html. Link each from UI_DESIGN.md with its
journey step, stories and R-xx. Re-check Gate G2 on the same branch and PR.
```

**3. Plan and agent rules**

```text
Run Stage 3. Write DEVELOPMENT_PLAN.md (features -> SPEC-xx of about 1-3 days
each, dependency order, the S-xx each frontend spec builds, parallel tracks, branch naming, the Cursor and Claude
workflow), TEST_STRATEGY.md (levels, tools, what runs per PR / nightly /
milestone, eval thresholds, conformance scenarios, Definition of Done,
pipeline and environments)
and DELIVERY_PLAN.md (M0, feature milestones as vertical slices with their
R-xx, hardening, RAID). Then write AGENTS.md, CLAUDE.md and
.cursor/rules/*.mdc per the Agent rules table, with frontmatter and ADR links.
Check Gate G3 and list the milestone scope I must agree with the client.
Branch docs/stage-3-plan, PR, update STATUS.md.
```

**4. Build: prepare a milestone** (then implement each spec in Cursor)

```text
Prepare milestone <Mx>: write plans/<Mx>/milestone.md and, for each of its
specs in DEVELOPMENT_PLAN.md, spec.md and prompt.md from the templates, with each frontend spec's S-xx
screens and its feat/SPEC-xx-<name> branch.
Check each spec against the Definition of Ready and order them by
dependency. Branch docs/<mx>-specs, PR, update STATUS.md.
```

For each spec: open its `prompt.md` in Cursor, run it with Composer 2.5 on `feat/SPEC-xx-<name>`, and open the PR. Then ask Claude:

```text
Review PR #<n> against plans/<Mx>/specs/<SPEC-xx>/spec.md, its S-xx screens, CLAUDE.md and the
spec Definition of Done. List blocking issues first, then suggestions.
Do not approve; I approve.
```

**5. Verify the milestone**

```text
Check milestone <Mx> against the exit checklist (G4), using STATUS.md, the
merged PRs and these results: <CI / E2E / eval links or pastes>. Mark each
item pass or fail with evidence, list open bugs by severity, and draft the
UAT script from the acceptance criteria of the milestone's R-xx.
```

**6. Release**

```text
Prepare release <vX.Y.0> for <Mx>: a RELEASE_NOTES.md entry in client
language, mapped to R-xx; CHANGELOG.md from the merged Conventional Commits;
RUNBOOK.md updates for the new flows (deploy, rollback, alerts, common
failures). Report the go-live checklist (G5). Branch docs/release-<vX.Y.0>, PR.
```

**7. Learn and change**

```text
Retro: write plans/retros/<Mx>.md from STATUS.md, the PR history and my
notes: <notes>. Cover what worked, what didn't, and actions with owners.
List proposed changes to PROCESS.md, the rules or the templates separately.
```

```text
Change request: the client sent <CR-xx / PRD v1.1>, now in docs/sources/.
Run change control: diff it against REQUIREMENTS.md, list the affected R-xx,
ADRs, contracts, screens, specs, tests and milestone dates, and estimate the impact.
Change no doc until I confirm.
```

## Quick start with a new PRD

Follow these eight steps to take a new PRD through the process for the first time.

1. Create an empty private GitHub repo for the product, set "Automatically delete head branches" and squash-only merging, and add the `main` ruleset (see CI/CD practices). Add required checks after M0 delivers CI.
2. In Claude, connect GitHub and install the Claude GitHub App on that repo, so threads can push branches and open PRs.
3. Export this doc as Markdown and save it as `PROCESS.md`.
4. Create a new Claude project. Attach the repo with push access, and upload `PROCESS.md` and the PRD as project files.
5. Paste the project instructions from the previous section, and fill in the product name, summary, PRD file name and repo.
6. In a new thread, run prompt 0 to bootstrap the repo, then merge its PR.
7. In another new thread, run prompt 1 for requirements intake. Review the requirements list and the open questions, get the questions answered, and send the follow-up prompt.
8. Run stage 2, then the screens prompts (2c: canvas, your review, then HTML), then stage 3, one thread each. Merge each PR before starting the next stage. Cursor starts only at stage 4, once the specs and rules exist.

On a first run, stages 1–3 show where the process or prompts need adjusting. Note those changes and fold them back into this doc after M0.
