# ADR-011: Cloud host for staging and production
Status: Proposed — awaiting your decision (Q-21)    Date: 2026-11-12

## Context
Five containers (ADR-001), managed PostgreSQL (ADR-006), S3-compatible storage with object lock (ADR-007), separate staging and production credentials (NFR-13), daily backups with RPO 24 h / RTO one working day (A-16), and a render container that needs several CPU cores and 4–8 GB memory for Chrome (NFR-12). One operator runs it, so operating effort matters as much as price. Data is the owner's account plus aggregate analytics (A-20); DPDP applicability is confirmed by a specialist (Q-20).

## Options

| | A. AWS Mumbai (ap-south-1) | B. Google Cloud Mumbai (asia-south1) | C. Developer PaaS + managed DB + R2 |
|---|---|---|---|
| Containers | ECS Fargate services (api, web, worker, render) | Cloud Run services (api, web); worker and render with always-allocated CPU or Cloud Run Jobs | Fly.io (has a Mumbai `bom` region) or Render/Railway |
| PostgreSQL | RDS PostgreSQL, automated snapshots, PITR | Cloud SQL PostgreSQL, PITR | Provider-managed PostgreSQL (check region and PITR) |
| Storage | S3 with Object Lock (native fit for ADR-007) | GCS (S3 interoperability is partial; retention lock differs) | Cloudflare R2 (S3 API; object lock support to verify) |
| Secrets | Secrets Manager / SSM | Secret Manager | Platform secrets |
| Ops effort | Highest: VPC, ALB, IAM, IaC (Terraform/CDK) | Medium: fewer moving parts; long-running worker needs care | Lowest: deploy from Dockerfiles |
| Fixed cost | Highest (RDS, ALB, NAT or VPC endpoints) | Medium | Lowest |
| Lock-in | Medium (Fargate, S3 portable) | Medium | Low |
| Risks | Setup time before M0 exit | DBOS worker and multi-minute renders fit Cloud Run's request model poorly | Regional capacity and managed-Postgres maturity vary by provider; one more vendor for storage |

## Recommendation
**A. AWS Mumbai**, deployed with Terraform from M0, because every hard requirement (object lock, PITR, long-running workers, per-environment IAM) is native and nothing in ADR-003 or ADR-007 needs a workaround. Choose **C** instead if lowest fixed cost and setup time matter more than those guarantees; then ADR-007's object lock becomes an application-level rule.

## Decision
Pending. Nothing is provisioned until you choose. The monthly cost estimate is written in TECH_STACK.md (Stage 2b) for the option you pick.

## Consequences
Whichever option: Docker images are the same everywhere (PROCESS CI/CD); the host is reached only through Terraform/config, not from application code.
