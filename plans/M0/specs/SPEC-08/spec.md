# SPEC-08: Telemetry wiring, Collector redaction and health checks
Milestone: M0 | Status: Draft (ready when SPEC-01a merges) | Layer: cross-cutting
Agent (if any): —
Requirements: NFR-09, NFR-06, NFR-15 | Feature: — (cross-cutting) | ADRs: ADR-016
Screens: — | Branch: `feat/SPEC-08-telemetry`

## Goal
Every service sends traces, metrics and JSON logs through the OpenTelemetry Collector to the local Grafana stack, with trace context carried across services and secrets and personal data removed twice.

## Scope
In:
- OpenTelemetry SDKs in `api`, `worker` (Python), `render` (Node), `web` (Next.js server and browser): OTLP to the Collector; resource attributes `service.name`, `service.version`, `deployment.environment`.
- Shared helpers per runtime to set the correlation attributes in [OBSERVABILITY.md](../../../../docs/architecture/OBSERVABILITY.md#conventions) (`oos.workspace_id`, `oos.project_id`, `oos.run_id`, …) and to inject and extract `traceparent` (HTTP headers; a field on outbox payloads for SPEC-09a to use).
- Logs: structlog (Python) and pino (Node) JSON with `trace_id`, `span_id`, `request_id`; redaction processors in both loggers.
- Collector config in `infra/otel/`: `transform`/`redaction` processors per the redaction table, span-attribute allowlist (unknown attributes dropped), retention 30 days logs and traces, 90 days metrics.
- `/healthz` and `/readyz` emit no spans (noise); readiness failures log `health.not_ready` with the failing dependency.
- Grafana provisioning in `infra/grafana/`: one "Stack health" dashboard (request rate, errors, duration per service; container up) and the PostgreSQL slow-query threshold (500 ms).

Out: flow-specific spans and panels (each spec adds its own); alerts (SPEC-82).

## Design
Conventions are owned by OBSERVABILITY.md and observability.mdc; this spec wires them. Expected diff: about 350 lines.

## Acceptance criteria
- AC1 (NFR-09): Given a browser request to a Studio page that calls `api`, when traced, then the web and api spans share one trace ID in Tempo.
- AC2 (NFR-06): Given a log line or span carrying an `Authorization` header, a key named like a secret, a signed URL query string or an email address, when it reaches Loki or Tempo, then the value is dropped or masked, even when the logger's own redaction is turned off for the test.
- AC3: Given a span attribute not on the allowlist, when exported, then it is dropped by the Collector.
- AC4 (NFR-15): Given the stack running, when Grafana opens, then the Stack health dashboard shows every service.

## Tests
- T-38 integration: trace continuity web → api now, extended to worker, agent and render by SPEC-13; Collector redaction and allowlist with logger redaction disabled (AC1–AC3). Runs nightly once SPEC-02 merges.
- Unit: logger redaction processors in both runtimes.

## Observability
This spec is the wiring. Update OBSERVABILITY.md only if a convention changes.

## Dependencies
SPEC-01a. Contracts: none. Size M (2 spec-days).
