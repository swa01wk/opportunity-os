# Observability

Status: **Draft for G2** (Stage 2b); a living doc after G2 for signals, and change-controlled for SLO targets. Every spec that adds a flow adds its spans, log events and dashboard panel here and in code (PROCESS Definition of Done). Stack: OpenTelemetry everywhere, one Collector, Grafana LGTM locally (ADR-016). KPI analytics events are a PostgreSQL projection (ADR-017). Requirements: NFR-09, NFR-15, NFR-06 (redaction), KPI-01–KPI-14.

## Conventions

- **One trace per user request.** The browser starts the trace; `traceparent` goes web → api → outbox event (`DomainEvent.traceparent`) → worker workflow → agent task / TTS / render job. A workflow started from an outbox row links to the request span; its long-running steps are child spans.
- **Correlation attributes** on every span, log and metric where they apply: `oos.workspace_id`, `oos.project_id`, `oos.run_id`, `oos.task_attempt_id`, `oos.workflow_type`, `oos.task_type`, `oos.gate`, `oos.artifact_sha256`, `oos.render_job_id`. These make NFR-09's "run → attempts → inputs → artifacts in one hop" possible.
- **AG-UI stream.** The relay span `relay.agui.emit` carries the trace of the event's source; each AG-UI run ID equals the execution run ID, so a run in the Studio links to its trace. Emitted events are logged (type, run ID, step) without payloads, so a session's stream can be reconstructed and replayed (ADR-020).
- **Names.** Spans `component.operation` (e.g. `api.approvals.record`, `agent.research.call_model`, `render.scene_clip`). Custom metrics prefixed `oos.` and follow OpenTelemetry semantic conventions for HTTP, DB and GenAI attributes (`gen_ai.request.model`, `gen_ai.usage.input_tokens`, `gen_ai.usage.output_tokens`).
- **Logs** are structured JSON (structlog in Python, pino in Node) with `trace_id`, `span_id`, `request_id` and the correlation attributes. Log events are named (`approval.refused`, `budget.paused`), not free text.
- **Money** in metrics is minor units of the reporting currency (INR) after conversion at the recorded rate (Q-05); the raw provider currency stays on the attempt record.

## Signals per component

| Component | Traces (spans) | Metrics | Log events |
|---|---|---|---|
| **web** (browser + Next.js server) | Page load, route change, API calls (fetch instrumentation), AG-UI stream connect | `oos.web.sse.reconnects`, `oos.web.agui.events{type}`, Web Vitals (LCP, INP) on Studio pages | `auth.callback_failed`, `sse.disconnected`, `agui.event_rejected` (fails the pinned schema) |
| **api** | Every request (`http.server`), DB queries, approval checks, preflight, revision impact | HTTP rate, errors, duration by route; `oos.approval.refused{reason}`; `oos.preflight.gaps{kind}`; `oos.idempotency.replays` | `approval.recorded`, `approval.refused`, `stale_version` (412), `authz.denied`, `export.built` |
| **worker: dispatcher + outbox relay** | `relay.deliver`, `workflow.start` | `oos.outbox.lag_seconds` (oldest undelivered), `oos.workflow_request.dispatch_seconds`, `oos.relay.delivered` | `workflow.duplicate_start_ignored`, `relay.retry` |
| **worker: workflows (DBOS)** | Workflow span with one child per step | `oos.run.duration_seconds{workflow_type,outcome}`, `oos.run.active`, `oos.run.stuck` (running > 2× expected), `oos.step.retries{step}`, `oos.queue.depth{queue}`, `oos.queue.wait_seconds{queue}` | `run.state_changed`, `run.paused_budget`, `run.takeover`, `run.cancelled`, `run.recovered_after_restart` |
| **worker: budget** | `budget.reserve`, `budget.settle` | `oos.cost.estimated_minor`, `oos.cost.actual_minor{provider,stage}`, `oos.cost.retry_minor` (spend on retried attempts), `oos.budget.remaining_minor{project}`, `oos.budget.overrun` (must stay 0) | `budget.reserved`, `budget.exhausted`, `budget.released` |
| **agent tasks** | `agent.<task>.run` → `call_model`, `tool.<name>` | Per task: `gen_ai` tokens, model latency, `oos.agent.tool_calls{tool}`, `oos.agent.failure{state}` (schema_invalid, citation_invalid, injection_detected, …), `oos.agent.budget_used_ratio` | `agent.output_rejected`, `agent.injection_detected`, `fetch.refused{reason}` |
| **media.audio (TTS, alignment)** | `tts.synthesize`, `audio.align`, `captions.segment` | Characters, latency, provider errors, `oos.narration.duration_delta_seconds` (measured vs planned) | `tts.pacing_change`, `tts.non_commercial_take` |
| **render service** | `render.job` → `compile`, `scene_clip`, `assemble`, `qa` (job span carries the trace from the worker) | `oos.render.duration_seconds{kind=preview|clip|master}`, `oos.render.cache_hit_ratio`, peak memory and CPU per job, `oos.render.limit_breach{limit}`, `oos.media_qa.failed{check}`, `oos.compiler.errors{code}` | `render.cache_hit`, `render.resource_limit`, `media_qa.failed` |
| **PostgreSQL** | DB spans from SQLAlchemy and DBOS | Connections, transaction rate, slow queries (> 500 ms), lock waits on `budget`, database size | `pg.slow_query` |
| **Object store** | `blob.put`, `blob.sign` | Bytes stored, put errors, signed URLs issued | `blob.hash_mismatch` |
| **Keycloak** | — | Login success and failure, MFA failures (Keycloak events) | Login and admin events (kept 1 year, A-30, SECURITY.md) |
| **Retention job** | `retention.sweep` | Objects deleted, bytes freed, referenced objects skipped | `retention.report` |
| **Backups** | `backup.run` | `oos.backup.age_seconds`, size, off-machine copy success | `backup.failed` |

Health: every container exposes `/healthz` (liveness) and `/readyz` (dependencies); Compose health checks use them.

## SLOs per key journey

All targets are **provisional — calibrate after R0** (A-15: no numeric performance targets until the R0 baseline, NFR-02). After R0 they are set here through change control. SLOs are **event-based**: they count requests or runs, not wall-clock time, because the local stack is not always running. Window: rolling 28 days. Client errors caused by invalid content (4xx, compiler errors, `invalid_content` class) do not count against an SLO; they are product signals.

| SLO | Journey (screen) | Indicator (good ÷ valid events) | Provisional target | Error budget |
|---|---|---|---|---|
| SLO-01 Studio responsiveness | All Studio screens (J1, J6) | API requests answered without 5xx and within 1 s (commands) or 500 ms (queries) | 99% — calibrate after R0 | 1% of requests |
| SLO-02 Dispatch | Any long action (J1) | Workflow requests started within 30 s of commit | 99% — calibrate after R0 | 1% |
| SLO-03 Live progress | Run indicator (J1, J6) | AG-UI events for committed domain events reaching the Studio stream within 5 s of commit | 99% — calibrate after R0 | 1% |
| SLO-04 Research | S-05 (J1) | Research runs reaching a reviewable ledger within 10 min without a platform failure | 90% — calibrate after R0 | 10% |
| SLO-05 Draft preview | S-07 (J1, J6) | Previews of a 30–60 s storyboard ready within 5 min | 90% — calibrate after R0 | 10% |
| SLO-06 Master render | S-11 (J1) | Masters rendered and QA-checked within 20 min | 90% — calibrate after R0 | 10% |
| SLO-07 Revision turnaround | S-09 → S-07 (J6) | Revision runs for a single-scene change finished within 10 min | 90% — calibrate after R0 | 10% |
| SLO-08 Run reliability | S-13 (J6) | Runs that end succeeded, paused (budget or approval) or cancelled, rather than failed from a platform cause | 95% — calibrate after R0 | 5% |
| SLO-09 No stuck runs | S-13 (J6) | Runs that never stay running beyond 2× their expected duration | 99% — calibrate after R0 | 1% |
| SLO-10 Export | S-11 (J1) | Export bundles built within 2 min | 99% — calibrate after R0 | 1% |

**Invariants (zero tolerance, not SLOs):** an alert fires on the first occurrence.

| Invariant | Signal |
|---|---|
| Spend never exceeds reservation and allowance (NFR-07) | `oos.budget.overrun > 0` |
| No effect executed under a stale or missing approval (R-41) | log event `authority.violation` from the step re-check |
| No approval or public action by a service or agent identity (R-43) | `oos.approval.refused{reason="non_member"}` rising, any `authority.violation` |
| No secret pattern in logs (NFR-06) | Collector redaction counter `oos.redaction.secret_matches > 0` after redaction (should be 0 because redaction runs first; a match means a new pattern) |
| Backups fresh (NFR-14) | `oos.backup.age_seconds > 36 h` |

## Alerts

Alerts are burn-rate alerts on the SLO error budgets (Google SRE multi-window, multi-burn-rate), provisioned from the repo into Grafana Alerting. Contact point: email from `.env` (ADR-016). Because event volume is small, every burn-rate rule also needs a minimum number of events in the short window (default 10) before it fires.

| Severity | Rule | Action |
|---|---|---|
| **Page** (email now) | Burn rate ≥ 14.4× over 1 h **and** over 5 min (2% of the 28-day budget in an hour) | Investigate today |
| **Page** | Burn rate ≥ 6× over 6 h **and** over 30 min | Investigate today |
| **Ticket** (daily digest) | Burn rate ≥ 1× over 3 days **and** over 6 h | Review at the next session |
| **Page** | Any invariant breach above | Stop and investigate; runbook entry |
| **Ticket** | Outbox lag > 5 min; queue wait > 10 min; render memory > 85% of cap; provider error ratio > 20% over 30 min; retry spend > 25% of a project's actual spend | Review |

RUNBOOK.md (hardening) gets one entry per page-level alert.

## Retention and PII redaction

**Retention** (Q-14, SECURITY.md; capped by disk on the owner's machine):

| Signal | Retention |
|---|---|
| Logs and traces | 30 days |
| Telemetry metrics | 90 days |
| Access audit (`audit_log`, Keycloak events) | 1 year (A-30; owned by SECURITY.md) |
| KPI analytics events | With the work they describe (ADR-017) |

**Redaction** runs twice: in the logger processors (structlog, pino) and again in the Collector (`transform` / `redaction` processors), so a missed field in code is still caught.

| Removed or masked | How |
|---|---|
| `Authorization` headers, cookies, `Set-Cookie` | Dropped |
| Provider API keys, client secrets, passwords | Dropped by key name; value patterns (`sk-…`, long base64/hex secrets) masked |
| Signed URLs and upload session URLs | Query string removed (`X-Amz-Signature`, `X-Amz-Credential`, tokens) |
| OAuth tokens (R3) | Dropped |
| Email addresses and display names | Masked; the member UUID is used for correlation instead |
| Prompt and model-output bodies, fetched page text | Never put in telemetry; prompts are identified by `prompt_sha256` and kept on the attempt record (R-50) |
| Narration text, script text | Not in telemetry; referenced by version ID |

Span attributes use an **allowlist** at the Collector: unknown attributes are dropped, so new attributes must be added on purpose.

## Product analytics events (per KPI-xx)

Written to `analytics.event` by the outbox relay from the listed domain event (ADR-017); never written directly. Contract: [analytics/events.schema.json](../contracts/analytics/events.schema.json) (0.2.0). Properties are typed and contain no free text or personal data beyond the member UUID. KPIs are SQL views over these events plus current state, shown on a "Validation" Grafana dashboard. R3 events arrive with the R3 spec.

| Analytics event | From domain event | Properties | KPIs |
|---|---|---|---|
| `video.approved` | `approval.recorded` where gate = D | projectId, series, packageVersionId, packageSha256, minutesSinceGateA | KPI-01, KPI-02, KPI-03, KPI-05 (denominator) |
| `video.published` | `publication.recorded` with observed public visibility | projectId, series, publicationId, route (`manual`), platform, verification (`NOT_CHECKED`/`PASSED`/`PARTIAL`/`FAILED`), packageMatch | KPI-01 |
| `gate.approved` | `approval.recorded` (A–E) | gate, responsibility, targetType, targetVersion, reopenedCount | Lead-time context for KPI-04 |
| `run.finished` | `run.state_changed` to a terminal state | runId, workflowType, outcome, attempts, codeRepairNeeded, manualTakeover | KPI-02 |
| `effort.logged` | `effort.recorded` | activity (incl. `code_repair`), minutes | KPI-02, KPI-04 |
| `kpi.baseline_recorded` | `kpi.baseline_recorded`, from `POST /kpi-baselines` (S-14) | kpi, minutes, revisions, costMinor, currency | KPI-04 |
| `cost.settled` | `budget.settled` | provider, stage, attemptOutcome (succeeded / failed / revised), estimatedMinor, actualMinor, currency, fxRate | KPI-05 |
| `rubric.scored` | `rubric.scored` | renderId, correctness, clarity, originality, readability, promisePayoff, mutedReviewPassed, allAtLeastThreshold | KPI-03, KPI-14 |
| `finding.resolved` | `finding.resolved` | severity, material, disposition | KPI-03 (zero unresolved material) |
| `metric.recorded` | `metric.snapshot_recorded` | publicationId, measure, value or null, availability, windowStart, windowEnd, denominator, source (`manual` at R2, `api` at R3), coldStart | KPI-06; at R3 KPI-07–KPI-11 and KPI-13 |
| `recommendation.decided` (R3) | added by the R3 spec | recommendationId, accepted, baselineChoice, outcomeObserved | KPI-12 |

**KPI → computation** (targets and owners stay in REQUIREMENTS.md):

| KPI | Computed as |
|---|---|
| KPI-01 Validation slate | Count of `video.published` per series vs 4/4/2/2 (also on S-16) |
| KPI-02 Production reliability | Approved videos with no `run.finished.codeRepairNeeded` and no `effort.logged` of `code_repair` ÷ approved videos; manual takeovers listed |
| KPI-03 Editorial quality | Approved videos whose final `rubric.scored` has every dimension ≥ 4, no unresolved material finding and no rights blocker at `video.approved` |
| KPI-04 Human effort | Sum of `effort.logged.minutes` per approved video vs `kpi.baseline_recorded` |
| KPI-05 Variable cost per approved output | Sum of `cost.settled.actualMinor` (all outcomes, incl. failed and revised) ÷ count of `video.approved`; fixed costs reported separately |
| KPI-06 Primary audience metric | `metric.recorded` for the A-09 measure at its 7-day window, labelled manual and cold-start |
| KPI-07–KPI-11 | `metric.recorded` by measure, compared within duration groups; R3 |
| KPI-12 Recommendation usefulness | `recommendation.decided` outcomes vs the editorial baseline choice; R3 |
| KPI-13 Growth study reach | Sum of `metric.recorded` views per upload in the study window; never presented as people (R-76); R3, conditional |
| KPI-14 Comprehension and readability | Share of approved videos whose final `rubric.scored.mutedReviewPassed` is true |

The `analytics` schema, the baseline entry path and these event names are in contracts 0.2.0 (`db/schema.sql`, `openapi.yaml`, `analytics/events.schema.json`).
