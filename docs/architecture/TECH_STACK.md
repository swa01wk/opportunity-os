# Tech stack

Status: **Draft for G2** (Stage 2b). Living summary: the reason for every choice is in its ADR; this file owns only the tool, the version line and the cost estimate. Layers follow ADR-001: **backend** (api, worker), **agent**, **media** (render service and `media/audio`), **web** (Studio).

**Versions.** The table gives the version line to use. Exact patch versions are pinned in the lockfiles (`uv.lock`, `pnpm-lock.yaml`) and image digests by the M0 repo spec, which also runs the dependency licence check (ADR-019). Lines marked ✓ were checked against the vendor's release page on 2026-11-13; the rest are the current stable line as known at writing and are confirmed at M0.

## Backend (api, worker)

| Tool | Version line | Use | ADR |
|---|---|---|---|
| Python | 3.13 | api, worker, agent, media/audio | ADR-001 |
| FastAPI + Uvicorn | FastAPI 0.1xx, Uvicorn 0.3x | REST API, SSE | ADR-004 |
| ag-ui-protocol | 0.1.x, exact pin in M0 | AG-UI event types and SSE encoding in the outbox relay | ADR-020 |
| Pydantic | 2.x | Canonical contracts; JSON Schema generation | ADR-008 |
| SQLAlchemy + psycopg | SQLAlchemy 2.0, psycopg 3 | Data access, row locks | ADR-004, ADR-006 |
| Alembic | 1.x | Migrations with tested downgrades | ADR-006 |
| DBOS Transact (Python) | 3.5 ✓ (MIT) | Durable workflows, queues; must pass the M0 restart spike | ADR-003 |
| PyJWT + JWKS client | 2.x | Access-token verification in `IdentityProvider` | ADR-012 |
| boto3 (S3 API only) | 1.x | `BlobStore` adapter | ADR-007, ADR-009 |
| structlog | 25.x | JSON logs with trace IDs and redaction | ADR-016 |

## Agent

| Tool | Version line | Use | ADR |
|---|---|---|---|
| OpenAI Python SDK | 2.x | `LlmProvider` adapter; structured outputs and function calling | ADR-014, ADR-009 |
| Model | `gpt-5.4-mini-2026-03-17` | Research, script, storyboard tasks; reasoning effort per task in config | ADR-014 |
| httpx | 0.2x | `SourceFetcher` (HTTPS only, SSRF-guarded, size-capped) | ADR-009 |
| trafilatura, pypdf | current | Text extraction from fetched HTML and PDF; run inside the task with size and time limits (SECURITY.md) | ADR-009 (confirmed in the M0 research spec) |
| Search API | open (Q-29) | `SearchProvider` behind an adapter; operator-supplied URLs until chosen | ADR-009 |
| Eval runner | in-repo (`agent/evals/`, pytest) | `make eval`: fake model by default, live with `LIVE=1` | ADR-014, ADR-019 |

## Media

| Tool | Version line | Use | ADR |
|---|---|---|---|
| Node.js | 24 LTS | render service | ADR-002 |
| Remotion (`@remotion/renderer`, `@remotion/player`, `@remotion/bundler`) | 4.0.x ✓ | Scene components, rendering, Studio preview | ADR-002 |
| Chrome Headless Shell | pinned by `npx remotion browser ensure` at image build | Rendering | ADR-002 |
| FFmpeg / ffprobe | bundled with Remotion | Encoding, concat, media checks | ADR-002 |
| KaTeX | 0.16.x | Equation typesetting, `trust: false` | ADR-002 |
| Ajv | 8.x | Runtime VideoSpec validation in the compiler | ADR-008 |
| pino | 9.x | JSON logs | ADR-016 |
| ElevenLabs API (via httpx) | "convert with timestamps"; `voiceId`, `modelId` pinned in config | Narration with character alignment, pronunciation dictionaries | ADR-013 |
| Alignment and caption segmentation | in-repo Python (`media/audio`) | Word and phrase timing, caption phrases | ADR-013 |
| Fonts | open-licence fonts, chosen with the house style; files and licences in the rights ledger | Captions, labels, equations | ADR-002, R-55 |

## Web (Studio)

| Tool | Version line | Use | ADR |
|---|---|---|---|
| Next.js (App Router) | 16.x ✓ | Studio | ADR-005 |
| React | 19.x | UI | ADR-005 |
| TypeScript | 5.x | web, media/scenes, contracts/ts | ADR-005, ADR-008 |
| Tailwind CSS | 4.x | Styling from tokens.md | ADR-018 |
| Radix UI primitives | current | Accessible dialogs, menus, tabs | ADR-018 |
| TanStack Query | 5.x | Server state, invalidated by AG-UI `CUSTOM` domain events | ADR-018, ADR-020 |
| @ag-ui/core | current, exact pin in M0 | AG-UI event types and schemas for the project stream | ADR-020 |
| openapi-typescript + openapi-fetch | current | Typed API client from `openapi.yaml` | ADR-018, ADR-004 |
| React Hook Form | 7.x | Forms | ADR-018 |
| Auth.js (generic OIDC) | 5.x | Sign-in with Keycloak / Cognito | ADR-012 |

## Data and storage

| Tool | Version line | Use | ADR |
|---|---|---|---|
| PostgreSQL | 17 (DDL also checked on 16) | `app`, `dbos`, `media`, `analytics` schemas | ADR-006, ADR-017 |
| Local S3-compatible store | interim: last MinIO CE image pinned by digest; replacement chosen in M0 | Artifacts, private, content-addressed | ADR-007, ADR-015 |
| Amazon S3 with Object Lock | — | After the R2 gate | ADR-007, ADR-011 |

## Identity

| Tool | Version line | Use | ADR |
|---|---|---|---|
| Keycloak | 26.8.x ✓ | Local OIDC, TOTP MFA; realm export without users or secrets | ADR-012 |
| Amazon Cognito | — | After the R2 gate | ADR-012 |

## Infrastructure and delivery

| Tool | Version line | Use | ADR |
|---|---|---|---|
| Docker Engine + Compose | Compose v2 | Local and staging stacks | ADR-011 |
| GNU make | 4.x | Single command surface (PROCESS) | ADR-019 |
| GitHub Actions | — | PR, main, nightly pipelines calling make targets | ADR-019 |
| uv, pnpm | current | Python and TS package management | ADR-019 |
| Ruff, mypy, ESLint (jsx-a11y), Prettier | current | Lint, types, format | ADR-019 |
| pytest, Testcontainers, Hypothesis, Vitest, Testing Library, Playwright, axe-core | current | Tests (levels in TEST_STRATEGY.md, Stage 3) | ADR-019 |
| gitleaks, pip-audit, pnpm audit, Semgrep OSS, Trivy, licence check | current | CI security scans | ADR-019 |
| Renovate | — | Dependency updates via PRs | ADR-019 |
| Terraform; ECS Fargate, RDS, S3, Secrets Manager, Cognito | — | AWS Mumbai after the R2 gate | ADR-011 |

## Observability

| Tool | Version line | Use | ADR |
|---|---|---|---|
| OpenTelemetry SDKs (Python, Node, browser) | current | Traces, metrics, logs | ADR-016 |
| OpenTelemetry Collector (contrib) | current | Single ingest point, redaction processors | ADR-016 |
| `grafana/otel-lgtm` (Grafana, Loki, Tempo, Prometheus-compatible) | current | Local backend, dashboards, alerting | ADR-016 |
| `analytics.event` in PostgreSQL | — | KPI events (OBSERVABILITY.md) | ADR-017 |

## Dependency licences to watch

| Dependency | Terms that matter | Status |
|---|---|---|
| Remotion | Free for individuals and companies of up to three people; otherwise a company licence | Owner licenses as an individual (Q-07, ADR-002). Re-check on any change of ownership. |
| DBOS Transact | MIT | Confirmed on PyPI, 2026-11-13 |
| MinIO CE (interim) | AGPL-3.0, no longer actively developed | Local only, replaced in M0 (ADR-015) |
| ElevenLabs output | No commercial licence on the free plan; paid-plan output stays usable after cancelling | Gate D blocks free-plan takes (ADR-013) |
| OpenAI API output | Owned by the customer under OpenAI's terms; data-use terms in SECURITY.md | Re-check at first real call |
| Fonts | Must allow embedding in published video | Recorded per font in the rights ledger (R-55) |

## Monthly cost estimate

Reporting currency INR. Estimates use **₹95 per USD**: the rupee closed at 94.46 on 5 Nov 2026 ([HDFC Sky](https://hdfcsky.com/news/rupee-settles-flat-at-94-46-against-us-dollar)), rounded up so the estimates do not understate cost. Actual costs never use this figure: each attempt records the rate on the day it is settled (Q-05). Q-05 budget limits stay parked: these numbers are planning estimates, not limits, and are replaced by measured per-video cost from R0 runs (KPI-05).

### Model and TTS usage per video

Assumptions: a 45–60 s Short; LLM list prices from ADR-014 (USD 0.75 per 1M input tokens, 4.50 per 1M output); ElevenLabs API overage price USD 0.08 per 1,000 characters for Multilingual v2 ([ElevenLabs API pricing](https://elevenlabs.io/pricing/api), 2026-11-13). Token counts are estimates until the R0 evaluation.

| Item | Typical per pass | Cost per pass (USD) | Ceiling per pass from tasks.json budgets (USD) |
|---|---|---|---|
| Research | 80k in, 8k out | 0.10 | 0.22 |
| Script | 20k in, 4k out | 0.03 | 0.08 |
| Storyboard | 60k in, 20k out | 0.14 | 0.26 |
| **LLM, one pass** | | **0.26** | **0.56** |
| **LLM, typical video** (one pass, one script and storyboard revision, half a research re-run) | | **0.48 (≈ ₹46)** | 1.68 if every task used its full budget three times (≈ ₹160) |
| Narration | ≈ 900 characters per full take; ≈ 4 take-equivalents with auditions and re-takes ≈ 3,600 characters | 0.29 at overage price (≈ ₹27); inside plan credits it is covered by the plan fee | — |
| Search (Q-29 open) | 20–50 queries | ≈ 0.10–0.25 placeholder | — |
| Render compute | local machine | 0 now | — |

### Now: local development (until the R2 gate)

| Line | Monthly | Notes |
|---|---|---|
| Infrastructure | ₹0 | Owner's machine (ADR-011); electricity and hardware not counted |
| LLM and TTS | ₹0 | Free credits in development (Q-05); cost still recorded per attempt |
| Off-machine backup copy | ₹0–200 | External disk or a small cloud bucket (NFR-14) |
| **During R2 validation (12 videos a month, published)** | **≈ ₹1,400 typical, up to ≈ ₹4,600** | Typical: LLM 12 × $0.48 + ElevenLabs Starter $6 (75,000 characters, enough for ≈ 20 videos at 3,600) + search ≈ $3. High: every task at full budget, ElevenLabs Creator $22, more search. A paid ElevenLabs plan is required before the first public upload (ADR-013). |

### Later: AWS Mumbai (after the R2 gate)

Indicative only. Compute uses us-east-1 Fargate list rates (USD 0.04048 per vCPU-hour, 0.004445 per GB-hour); ap-south-1 rates differ by a few percent and are confirmed with the AWS Pricing Calculator in the AWS migration spec.

| Line | Sizing assumption | USD / month |
|---|---|---|
| ECS Fargate, production, always on | web 0.5 vCPU/1 GB, api 0.5/1 GB, worker 1/2 GB | ≈ 72 |
| ECS Fargate, render, on demand | 4 vCPU/8 GB, ≈ 20 h a month | ≈ 4 |
| ECS Fargate, staging | scaled to zero outside use (≈ 25%) | ≈ 19 |
| RDS PostgreSQL | db.t4g.small single-AZ production + db.t4g.micro staging, 20 GB gp3 each, PITR backups | ≈ 45–60 |
| S3 | ≈ 50 GB with Object Lock, requests | ≈ 3 |
| Application Load Balancer | one, shared by staging and production | ≈ 20–25 |
| NAT gateway | one (or VPC endpoints instead; decided in the migration spec) | ≈ 35–45 |
| Secrets Manager, KMS | ≈ 10 secrets, one key | ≈ 5 |
| Logs and metrics | CloudWatch or self-hosted Grafana stack (ADR-016) | ≈ 10–25 |
| Cognito, Route 53, ECR, data transfer | one user; small volumes | ≈ 3–5 |
| **Infrastructure total** | | **≈ 215–265 (≈ ₹20,500–25,000)** |
| Model, TTS, search usage | 12 videos a month, as above | ≈ 15–50 (≈ ₹1,400–4,600) |
| **All in** | | **≈ 230–315 (≈ ₹22,000–30,000)** |

Largest levers if this is too high: Graviton (ARM) tasks, no NAT gateway, staging off by default, a single RDS instance with two databases. They are decided in the AWS migration spec, not now.
