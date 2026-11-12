# ADR-011: Local first; AWS Mumbai when hosting is needed
Status: Accepted    Date: 2026-11-12 (decided by the product owner; Q-21)

## Context
The system runs five containers (ADR-001), PostgreSQL (ADR-006) and S3-compatible storage with object lock (ADR-007). Hosted needs are separate staging and production credentials (NFR-13), daily backups with RPO 24 h and RTO one working day (A-16, NFR-14) and alerting (NFR-15). One person operates it. The data is the owner's account plus aggregate analytics (A-20).

Options proposed in Stage 2a: AWS Mumbai, Google Cloud Mumbai, or a developer PaaS (Fly.io / Render / Railway + Cloudflare R2).

## Decision
- **Now: local only.** The whole stack runs on the owner's machine with Docker Compose: web, api, worker, render, PostgreSQL, MinIO (object lock and versioning on) and Keycloak (ADR-012). No cloud account is provisioned.
- **When it scales: AWS Mumbai (ap-south-1)**, deployed with Terraform. The target shape is ECS Fargate services for web, api, worker and render, RDS PostgreSQL with point-in-time restore, S3 with Object Lock, Secrets Manager and Cognito (ADR-012).
- When AWS is introduced is a delivery-plan decision, set at G3 (Stage 3). It is not tied to a date here.

## Alternatives
- **Google Cloud Mumbai:** the long-running DBOS worker and multi-minute renders fit Cloud Run's request model poorly.
- **Developer PaaS + R2:** lowest cost, but object lock, point-in-time restore and long-running workers need workarounds.
- **AWS from day one:** fixed cost and setup time before there is anything to host.

## Consequences
- Easier: no cloud spend or setup during early milestones; the same Docker images move to AWS unchanged.
- Harder: until AWS exists, the hosted parts of NFR-13 (staging), NFR-14 (restore rehearsal) and NFR-15 (alerting) cannot be verified. Locally, backup is a scheduled `pg_dump` plus a MinIO bucket copy, and a restore is rehearsed from them.
- Must do: keep everything host-neutral. That means the S3 API only (no MinIO-specific calls), configuration from the environment, and no AWS SDK outside the adapters. The project brief describes R1 as a hosted release, so the delivery plan must put AWS provisioning before R1 acceptance. This is flagged for G3.
- Cost estimate: TECH_STACK.md (Stage 2b) gives local cost as zero infrastructure plus provider usage, and an AWS estimate for later.
