# ADR-016: OpenTelemetry everywhere; Grafana LGTM stack locally
Status: Accepted    Date: 2026-11-13

## Context
ARCHITECTURE.md left the telemetry backend to Stage 2b. NFR-09 needs run, task, attempt, content and artifact IDs linked in traces; NFR-15 needs dashboards and alerts on stuck runs, render time and memory, provider errors, retry spend and publication uncertainty. Local only until the R2 gate (ADR-011), one operator, small volume. PROCESS asks for OpenTelemetry spans frontend → backend → agent → database with one trace per request.

## Decision
- **Instrumentation:** OpenTelemetry SDKs in every runtime (Python: api, worker, agent, media.audio; Node: render; browser and Next.js server: web). W3C `traceparent` crosses web → api → outbox (`traceparent` field on DomainEvent) → worker → render job.
- **Collector:** one OpenTelemetry Collector container; all signals go through it, where redaction processors run (OBSERVABILITY.md).
- **Local backend:** the `grafana/otel-lgtm` single image (Grafana, Loki logs, Tempo traces, Prometheus-compatible metrics) in Docker Compose, with dashboards and alert rules provisioned from the repo. Alerts go to an email contact point configured in `.env`.
- **AWS later:** keep the Collector; choose the backend (self-hosted Grafana stack on ECS, or CloudWatch / Amazon Managed Grafana) in the AWS migration spec. Instrumentation does not change.
- **Product analytics are not telemetry** (ADR-017).

## Alternatives
- **Separate Jaeger + Prometheus + Loki containers:** more to configure for the same result locally.
- **SaaS observability (Grafana Cloud, Honeycomb, Datadog):** data leaves the machine; another vendor before there is a hosted product.
- **Logs only:** cannot satisfy NFR-09's linked traces.

## Consequences
- Easier: one standard; backend swap is a Collector config change.
- Harder: the LGTM image is meant for development; its retention and disk use are capped in config (OBSERVABILITY.md).
