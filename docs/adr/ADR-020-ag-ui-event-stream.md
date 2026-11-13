# ADR-020: AG-UI events on the Studio's project event stream
Status: Accepted (tech lead, 13 Nov 2026; owner to confirm at G2)    Date: 2026-11-13

## Context
The Studio follows long-running work (research, script, storyboard, narration, preview, master, revision) on one SSE stream per project, `GET /projects/{projectId}/events`. Until now each `data:` line was a raw DomainEvent (ADR-010), and the Studio worked out run progress from event types. PROCESS.md now makes AG-UI the standard contract between agents and the UI for agentic products, so that run lifecycle, steps, tool activity and state recovery use one shared vocabulary. Requirements: R-50 (run and attempt records), R-53 (actionable errors), R-61 (honest states), SLO-03 (live progress), NFR-01, NFR-09.

OpportunityOS has no chat at R1–R2 (A-28). Its agents run inside durable workflows (ADR-003) that outlive any browser connection.

## Decision
- The project event stream emits **AG-UI events** (SSE encoding), produced by the outbox relay with the AG-UI Python SDK (`ag-ui-protocol`) and read in the Studio with `@ag-ui/core` types. Both are pinned in the M0 lockfiles.
- **Observe, don't hold.** Runs are started by REST commands (202) and observed on the stream: thread ID = project ID, run ID = execution run ID. The AG-UI run request (client POSTs input and holds the stream) is not used at R1–R2.
- **Mapping:**
  - run lifecycle → `RUN_*`;
  - workflow steps and task attempts → `STEP_*`;
  - agent tool calls → summarised `TOOL_CALL_*`;
  - render progress and pauses → `ACTIVITY_*`;
  - reconnect → `STATE_SNAPSHOT`;
  - every DomainEvent → `CUSTOM` named `opportunityos.<type>`, so ADR-018's query invalidation keeps working.

  Defined in `docs/contracts/agui/stream.json` (contracts 0.3.0).
- Events carry no authority. Approvals and every other consequential command stay REST commands with `If-Match` and version hashes (R-40, R-41, R-43).

## Alternatives
- **Keep raw DomainEvents on SSE.** Works, but every agentic product would invent its own progress vocabulary, and a later chat feature (R-64) would need a second stream format.
- **Full AG-UI run request per command.** Ties a durable run to one HTTP connection; a closed tab or token refresh would cut the run's stream, and resuming would need custom logic anyway.
- **CopilotKit runtime and UI components.** Useful for chat. At R1–R2 there is no chat, so it would add a framework for no user-facing need; reconsider with R-64.
- **WebSocket transport.** Not needed: the stream is server-to-client only; SSE matches the existing endpoint and `Last-Event-ID` resume.

## Consequences
- Easier:
  - one documented event vocabulary for run indicator, S-13 and error panels;
  - recorded streams become test fixtures;
  - R-64 chat could later reuse the same protocol and client types.
- Harder:
  - the relay maps domain events to AG-UI events and must keep the mapping in step with `domain-event.schema.json`;
  - AG-UI is pre-1.0, so upgrades are their own spec.
- Must do:
  - contracts 0.3.0 (`agui/stream.json`, stream description in `openapi.yaml`);
  - TECH_STACK rows;
  - SECURITY TH-31 and TH-32;
  - OBSERVABILITY stream signals;
  - the M0 relay spec includes the mapping and a replayed-stream Playwright test.
