# ADR-020: AG-UI events on the Studio's project event stream
Status: Accepted (tech lead, 14 Nov 2026; owner to confirm at G2)    Date: 2026-11-14

## Context
The Studio follows long-running work (research, script, storyboard, narration, preview, master, revision) on one SSE stream per project, `GET /projects/{projectId}/events`. Until now each `data:` line was a raw DomainEvent (ADR-010), and the Studio inferred run progress from event types, with no resume cursor beyond the event ID.

PROCESS.md (Agent architecture) makes AG-UI the interaction-plane contract for agentic products. It requires commands, observations and state to stay separate; a replay cursor with sequence checks; auth renewal; redaction; legible waiting and blocked states; and no executable UI from agents (topic 9 of the agent decisions). Requirements: R-50 (run and attempt records), R-53 (actionable errors), R-61 (honest states), SLO-03 (live progress), NFR-01, NFR-09.

OpportunityOS has no chat at R1–R2 (A-28). Its agents run inside durable workflows (ADR-003) that outlive any browser connection.

## Decision
- The project event stream emits **AG-UI events** (SSE encoding), produced by the outbox relay with the AG-UI Python SDK (`ag-ui-protocol`) and read in the Studio with `@ag-ui/core` types. Both are pinned in the M0 lockfiles.
- **Observe, don't hold.** Runs are started by REST commands (202) and observed: thread ID = project ID, run ID = execution run ID. The AG-UI run request is not used at R1–R2.
- **Projection, not source.** AG-UI events are projected from DomainEvents and attempt spans:
  - run lifecycle → `RUN_*`;
  - workflow steps and task attempts → `STEP_*`;
  - agent tool calls → summarised `TOOL_CALL_*`;
  - render progress and pauses (budget, gate, takeover, cancelling) → `ACTIVITY_*`;
  - connect and reconnect → `STATE_SNAPSHOT` with active runs and blockers;
  - every DomainEvent → `CUSTOM` named `opportunityos.<type>`, so ADR-018's query invalidation keeps working.
- **Cursor.** A new `outbox_event.seq` (bigserial) is the SSE `id:`; span-derived events use `<seq>.<n>`. `Last-Event-ID` resumes after the cursor; the client drops duplicates and reconnects on a gap.
- **No authority, no generated UI.** Approvals and every other consequential command stay REST commands with `If-Match` and version hashes (R-40, R-41, R-43). Agents cannot request UI components.
- **Redaction and scope.** Events carry summaries and IDs only; the stream is authorised per workspace and project and closes when the token expires.

Defined in `docs/contracts/agui/stream.json` (contracts 0.3.0), applied in [AGENT_ARCHITECTURE.md](../architecture/AGENT_ARCHITECTURE.md#ag-ui-in-opportunityos).

## Alternatives
- **Keep raw DomainEvents on SSE.** Works, but every product would invent its own progress vocabulary, and a later chat feature (R-64) would need a second format.
- **Full AG-UI run request per command.** Ties a durable run to one HTTP connection; a closed tab or token refresh would cut its stream.
- **CopilotKit runtime and components.** Useful for chat; at R1–R2 there is no chat, so it adds a framework for no user need. Reconsider with R-64.
- **WebSocket transport.** Not needed: the stream is server-to-client only, and SSE has `Last-Event-ID` resume.

## Consequences
- Easier:
  - one documented event vocabulary for the run indicator, S-13 and error panels;
  - reconnects rebuild state from snapshot plus cursor (conformance C10);
  - recorded streams become test fixtures; R-64 chat could reuse the protocol.
- Harder:
  - the relay keeps the mapping in step with `domain-event.schema.json`;
  - AG-UI is pre-1.0, so upgrades are their own spec.
- Must do:
  - contracts 0.3.0 (`agui/stream.json`, examples, `outbox_event.seq`, stream description in `openapi.yaml`);
  - TECH_STACK rows; SECURITY TH-31, TH-32; OBSERVABILITY stream signals;
  - the M0 relay spec includes the mapping, a field check against the pinned SDK and a replayed-stream Playwright test.
