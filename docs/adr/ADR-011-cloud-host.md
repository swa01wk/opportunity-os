# ADR-011: Local first; AWS Mumbai when hosting is needed
Status: Accepted · Local store amended by ADR-015    Date: 2026-11-12 (decided by the product owner; Q-21)

## Context
The system runs five containers (ADR-001), PostgreSQL (ADR-006) and S3-compatible storage with object lock (ADR-007). Hosted needs are separate staging and production credentials (NFR-13), daily backups with RPO 24 h and RTO one working day (A-16, NFR-14) and alerting (NFR-15). One person operates it. The data is the owner's account plus aggregate analytics (A-20).

Options proposed in Stage 2a: AWS Mumbai, Google Cloud Mumbai, or a developer PaaS (Fly.io / Render / Railway + Cloudflare R2).

## Decision
- **Now: local only.** The whole stack runs on the owner's machine with Docker Compose: web, api, worker, render, PostgreSQL, MinIO (object lock and versioning on) and Keycloak (ADR-012). No cloud account is provisioned.
- **When it scales: AWS Mumbai (ap-south-1)**, deployed with Terraform. The target shape is ECS Fargate services for web, api, worker and render, RDS PostgreSQL with point-in-time restore, S3 with Object Lock, Secrets Manager and Cognito (ADR-012).
- **When:** after the product objective is met, read as the R2 gate: the 12-video validation slate approved and published (KPI-01). Owner decision, 2026-11-13. R1 and R2 are accepted on the local environment.

## Alternatives
- **Google Cloud Mumbai:** the long-running DBOS worker and multi-minute renders fit Cloud Run's request model poorly.
- **Developer PaaS + R2:** lowest cost, but object lock, point-in-time restore and long-running workers need workarounds.
- **AWS from day one:** fixed cost and setup time before there is anything to host.

## Consequences
- Easier: no cloud spend or setup during early milestones; the same Docker images move to AWS unchanged.
- Harder: NFR-13, NFR-14 and NFR-15 are met locally until then. Staging is a second Compose environment with its own credentials and bucket. Backup is a scheduled `pg_dump` plus a MinIO bucket copy, and a restore is rehearsed from them. Alerts go to a local OpenTelemetry stack (OBSERVABILITY.md, Stage 2b). The machine itself is a single point of failure, so backups are also copied off the machine.
- Must do: keep everything host-neutral. That means the S3 API only (no MinIO-specific calls), configuration from the environment, and no AWS SDK outside the adapters. The AWS move is its own milestone after the R2 gate in DELIVERY_PLAN.md (Stage 3).
- Cost estimate: TECH_STACK.md (Stage 2b) gives local cost as zero infrastructure plus provider usage, and an AWS estimate for later.
