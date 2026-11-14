# SPEC-10: AG-UI relay and project event stream (ADR-020)
Milestone: M0 | Status: Draft (ready when SPEC-06 and SPEC-09a merge) | Layer: backend
Agent (if any): —
Requirements: R-50, R-61, NFR-04 | Feature: F-14, F-17 | ADRs: ADR-020, ADR-010, ADR-012
Screens: — | Branch: `feat/SPEC-10-agui-relay`

## Goal
The Studio can open one authorised SSE stream per project and follow every run as AG-UI events, resuming after a drop from its cursor with a state snapshot and no duplicates.

## Scope
In:
- Pin `ag-ui-protocol` (Python) and `@ag-ui/core` (in `web/package.json`) to exact versions (TECH_STACK.md "exact pin in M0").
- Mapping in `backend/opportunityos/workflows/agui.py`: a pure function from an outbox DomainEvent (and its attempt summary) to AG-UI events, per the `x-agui` mapping in [agui/stream.json](../../../../docs/contracts/agui/stream.json): run lifecycle → `RUN_*`; task attempts and workflow steps → `STEP_*`; every DomainEvent → `CUSTOM` `opportunityos.<type>`; IDs `<seq>` or `<seq>.<n>`. Tool-call and activity mappings are implemented for the shapes in the contract and exercised by the recorded streams.
- `GET /v1/projects/{projectId}/events` (SSE) in `api`: authenticates (SPEC-06), checks the member's workspace owns the project (else 404, audited), sends `STATE_SNAPSHOT` (active runs, blockers, `asOfSeq`) then mapped events with `seq > Last-Event-ID`; heartbeat comments; closes when the access token expires.
- Delivery: the outbox relay (SPEC-09a) adds a sink that issues `NOTIFY` after delivery; stream handlers wake on it and read the outbox by cursor, so replay and live use the same path. The outbox is the only source (ADR-020 "projection, not source").
- Field allowlist on every emitted payload: IDs, names, counts, coded reasons; never prompt, page, script or narration text, secrets or signed URLs.

Out: the Studio client, run indicator and gap handling in the browser (SPEC-34; SPEC-13 has a minimal client); render progress activity events (SPEC-23).

## Design
- Mapping runs where the stream is served (the API reads the outbox by cursor and maps on read) rather than storing AG-UI frames; this keeps one source and a replayable cursor. If you read ADR-020 as requiring frames to be stored, say so in review.
- Expected diff: about 420 lines; at the upper bound, so if the tool-call and activity mappings push it past about 450, split them into a follow-up spec before opening the PR.

## Acceptance criteria
- AC1 (R-50): Given a run's DomainEvents in the outbox, when streamed, then the client receives `RUN_STARTED`, `STEP_*` and `RUN_FINISHED` (or `RUN_ERROR`) with run ID = execution run ID and thread ID = project ID, and a `CUSTOM` event per DomainEvent.
- AC2 (C10): Given a client that reconnects with `Last-Event-ID: 245`, when the stream resumes, then it starts with `STATE_SNAPSHOT` and then only events with cursor greater than 245, in order, with none repeated.
- AC3 (NFR-04, C07): Given a member of workspace A, when they open the stream of a project in workspace B, then 404, nothing is streamed and `authz.denied` is audited.
- AC4: Given an open stream whose token expires, then the server closes it; reconnecting with a new token and `Last-Event-ID` resumes without loss.
- AC5: Given any emitted event, then its payload fields are on the allowlist and validate against the pinned SDK types and `agui/stream.json`.

## Tests
- T-39 contract: mapping output and the four recorded streams validate against the pinned `ag-ui-protocol` and `@ag-ui/core` types; field allowlist (AC1, AC5).
- T-10 contract and functional (C10, server part): reconnect with a cursor after dropped events gives snapshot plus ordered, de-duplicated events (AC2, AC4). The Playwright replay part is SPEC-34's.
- T-07 functional (C07, stream part): cross-workspace stream refused and audited (AC3).

## Observability
Span `relay.agui.emit` carrying the source event's trace; metrics `oos.agui.first_event_seconds`, stream connections and reconnects; events logged with type, run ID, cursor and step, never payloads (OBSERVABILITY.md AG-UI stream). Add a stream panel to the Stack health dashboard.

## Dependencies
SPEC-06 (auth), SPEC-09a (outbox relay), SPEC-03b (generated stream and event types). Contracts: 1.0.0. Size L (3 spec-days).
