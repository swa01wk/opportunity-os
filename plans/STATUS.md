# STATUS: OpportunityOS        Updated: 2026-11-14
Current stage: 4 Build M0 (SPEC-01a merged #13; next SPEC-03a and SPEC-02) | Next gate: G4 M0 exit

Release target: R0 -> R1 -> R2 (PRD Section 4). R3 conditional; R4/R5 out of scope.

## Stages and gates

All gates are signed by the product owner / tech lead (same person).

| Stage | Gate | Status | Signed | PR |
|---|---|---|---|---|
| 0 Bootstrap | — | Done (merged 2026-11-12) | — | chore/bootstrap, #1 |
| 1 Intake | G1 Requirements baseline | Signed | 2026-11-12 | docs/stage-1-intake, #2 |
| 2 Design | G2 Design review and screens | Signed: 2a, 2b, 2c merged (HTML prototypes S-01–S-16 in #7); all G2 checks pass | 2026-11-14 | docs/stage-2a-architecture, #3 · docs/stage-2b-design, #4 · design/screens-v1, #5, #7 |
| 3 Plan | G3 Milestone scope and dates | Signed: plan (#8), Strategy v1.0 intake (#9, #10); Q-36–Q-42 decided; all G3 checks pass; milestones not dated (Q-36) | 2026-11-14 | docs/stage-3-plan, #8 · docs/strategy-v1-intake, #9 |
| 4 Prepare M0 | — (Definition of Ready per spec; G4 at M0 exit) | Prepared and merged 2026-11-14: [plans/M0/milestone.md](M0/milestone.md) and 21 specs with prompts; Q-43 accepted; splits confirmed. Building: SPEC-01a merged (#13) | — | docs/m0-specs, #12 · feat/SPEC-01a-toolchain, #13 |

| Milestone | Scope | Status | Exit date |
|---|---|---|---|
| M0 | Foundation: walking skeleton: 21 specs, 39 spec-days | In progress: 1 of 21 specs merged (SPEC-01a) | Not dated (Q-36); forecast 5 Feb 2027 |
| M1 | Feasibility (R0): 11 specs, 28 spec-days | Planned | Not dated (Q-36); forecast 26 Mar 2027 |
| M2 | Brief to evidence (R1): 15 specs, 33 spec-days | Planned | Not dated (Q-36); forecast 21 May 2027 |
| M3 | Script to preview (R1): 12 specs, 26 spec-days | Planned | Not dated (Q-36); forecast 9 Jul 2027 |
| M4 | Master to export (R1): 8 specs, 19 spec-days | Planned | Not dated (Q-36); forecast 13 Aug 2027 |
| M5 | Revision and recovery (R1 gate): 9 specs, 22 spec-days | Planned | Not dated (Q-36); forecast 1 Oct 2027 |
| M6 | Channel record (R2 features): 7 specs, 13 spec-days | Planned | Not dated (Q-36); forecast 29 Oct 2027 |
| M7 | Hardening, go-live (G5): 7 specs, 12 spec-days | Planned | Not dated (Q-36); forecast 19 Nov 2027 |
| R2 slate | Twelve originals 4/4/2/2 published; R2 gate | Planned | Not dated (Q-36); forecast 14 Jan 2028 |

Scope, slices, exit criteria and RAID: [DELIVERY_PLAN.md](DELIVERY_PLAN.md). Specs: [DEVELOPMENT_PLAN.md](DEVELOPMENT_PLAN.md). Tests and pipeline: [TEST_STRATEGY.md](TEST_STRATEGY.md).

## Current milestone specs

M0, prepared in Stage 4: [plans/M0/milestone.md](M0/milestone.md) (dependency groups, Definition of Ready check, splits). Each spec's `spec.md` and Cursor `prompt.md` are in `plans/M0/specs/SPEC-xx/`. Listed in dependency order.

| Spec | Requirements | Screens | Branch / PR | Status | Owner |
|---|---|---|---|---|---|
| [SPEC-01a Repo toolchain, Makefile and Compose stack](M0/specs/SPEC-01a/spec.md) | NFR-13 | — | `feat/SPEC-01a-toolchain`, [#13](https://github.com/swa01wk/opportunity-os/pull/13) | Done (merged 2026-11-14; T-31 passed) | Owner (Claude) |
| [SPEC-01b Release host: make release and deploy to local staging](M0/specs/SPEC-01b/spec.md) | NFR-13 | — | `feat/SPEC-01b-release-host` | Ready | Owner (Cursor) |
| [SPEC-02 CI pipeline, security scans and branch rules](M0/specs/SPEC-02/spec.md) | NFR-05, NFR-06, NFR-13, NFR-18 | — | `feat/SPEC-02-ci-pipeline` | Ready | Owner (Cursor) |
| [SPEC-03a Contracts I: pipeline, drift, dual-runtime fixtures, common, workflow requests](M0/specs/SPEC-03a/spec.md) | NFR-19, NFR-11 | — | `feat/SPEC-03a-contracts-pipeline` | Ready | Owner (Cursor) |
| [SPEC-05 Object store choice and BlobStore adapter (ADR-015 amendment)](M0/specs/SPEC-05/spec.md) | R-30, NFR-04 | — | `feat/SPEC-05-object-store` | Ready | Owner (Cursor) |
| [SPEC-08 Telemetry wiring, Collector redaction and health checks](M0/specs/SPEC-08/spec.md) | NFR-09, NFR-06, NFR-15 | — | `feat/SPEC-08-telemetry` | Ready | Owner (Cursor) |
| [SPEC-03b Contracts II: domain events, AG-UI stream, analytics](M0/specs/SPEC-03b/spec.md) | NFR-19, R-50 | — | `feat/SPEC-03b-contracts-events` | Draft: needs SPEC-03a | Owner (Cursor) |
| [SPEC-03c Contracts III: agent task, execution and tool contracts](M0/specs/SPEC-03c/spec.md) | NFR-19, R-63 | — | `feat/SPEC-03c-contracts-agent` | Draft: needs SPEC-03a | Owner (Cursor) |
| [SPEC-03d Contracts IV: media contracts](M0/specs/SPEC-03d/spec.md) | NFR-19, R-18 | — | `feat/SPEC-03d-contracts-media` | Draft: needs SPEC-03a | Owner (Cursor) |
| [SPEC-04 Database baseline, migrations, service roles and RLS](M0/specs/SPEC-04/spec.md) | R-01, NFR-04, NFR-13 | — | `feat/SPEC-04-database` | Draft: needs SPEC-01a, SPEC-03a | Owner (Cursor) |
| [SPEC-03e Contracts V: Studio API models, OpenAPI drift, TS client, contracts 1.0.0](M0/specs/SPEC-03e/spec.md) | NFR-19, NFR-11 | — | `feat/SPEC-03e-contracts-api` | Draft: needs SPEC-03b–03d | Owner (Cursor) |
| [SPEC-09a Write path: idempotency, audit, outbox and workflow dispatch](M0/specs/SPEC-09a/spec.md) | NFR-01, R-50 | — | `feat/SPEC-09a-outbox` | Draft: needs SPEC-04, SPEC-03b, SPEC-08 | Owner (Cursor) |
| [SPEC-12 Render service skeleton, job API and resource limits](M0/specs/SPEC-12/spec.md) | R-29, NFR-12 | — | `feat/SPEC-12-render-skeleton` | Draft: needs SPEC-03d, SPEC-05 | Owner (Cursor) |
| [SPEC-06 API authentication, members and responsibilities](M0/specs/SPEC-06/spec.md) | R-01, R-05, NFR-04 | — | `feat/SPEC-06-api-auth` | Draft: needs SPEC-04, SPEC-03e | Owner (Cursor) |
| [SPEC-09b DBOS kill-and-resume spike (ADR-003)](M0/specs/SPEC-09b/spec.md) | NFR-01, R-50, R-51 | — | `feat/SPEC-09b-dbos-spike` | Draft: needs SPEC-09a | Owner (Cursor) |
| [SPEC-07 Studio sign-in and app shell](M0/specs/SPEC-07/spec.md) | R-01, R-05, R-61 | S-01 | `feat/SPEC-07-studio-shell` | Draft: needs SPEC-06 | Owner (Cursor) |
| [SPEC-10 AG-UI relay and project event stream (ADR-020)](M0/specs/SPEC-10/spec.md) | R-50, R-61, NFR-04 | — | `feat/SPEC-10-agui-relay` | Draft: needs SPEC-06, SPEC-09a | Owner (Cursor) |
| [SPEC-11a Agent runtime, tool host, validation stages, fake model (ADR-021)](M0/specs/SPEC-11a/spec.md) | R-63, NFR-05, NFR-11 | — | `feat/SPEC-11a-agent-runtime` | Draft: needs SPEC-03c, SPEC-09b | Owner (Cursor) |
| [SPEC-11b OpenAI LlmProvider adapter, portability fixtures, eval runner](M0/specs/SPEC-11b/spec.md) | NFR-11, R-63 | — | `feat/SPEC-11b-openai-adapter` | Draft: needs SPEC-11a | Owner (Cursor) |
| [SPEC-13 Walking skeleton, traced and deployed to staging](M0/specs/SPEC-13/spec.md) | NFR-09, NFR-13 | S-01 | `feat/SPEC-13-walking-skeleton` | Draft: needs six specs | Owner (Cursor) |
| [SPEC-14 Search API choice and SearchProvider adapter (Q-29)](M0/specs/SPEC-14/spec.md) | R-08, NFR-11 | — | `feat/SPEC-14-search-provider` | Draft: needs SPEC-11a | Owner (Cursor) |

## Screens
Designed by journey on the [Claude Design canvas](https://claude.ai/artifact/6jStrLtkcRDG5GfEf5g8HS) (journey map, what it solves, J1, J6, J3), approved by you on 2026-11-14. Each approved screen has a self-contained HTML prototype with its empty, loading and error states (PROCESS.md, Stage 2 screens).

| Screen | Requirements | Specs | Status |
|---|---|---|---|
| S-01 Sign-in and app shell | R-01, R-05 | SPEC-07, SPEC-13, SPEC-34, SPEC-35 | Approved (canvas, 2026-11-14); HTML [S-01-shell.html](../docs/design/screens/S-01-shell.html) |
| S-02 Projects | R-01, R-44 | SPEC-36 | Approved (canvas, 2026-11-14); HTML [S-02-projects.html](../docs/design/screens/S-02-projects.html) |
| S-03 Brief and preflight | R-06, R-07, R-57, Gate A | SPEC-38 | Approved (canvas, 2026-11-14); HTML [S-03-brief.html](../docs/design/screens/S-03-brief.html) |
| S-04 Project settings and data | R-02–R-04, R-34, R-56, R-60 | SPEC-37, SPEC-68, SPEC-73 | Approved (canvas, 2026-11-14); HTML [S-04-settings.html](../docs/design/screens/S-04-settings.html) |
| S-05 Evidence | R-08–R-10 | SPEC-39 | Approved (canvas, 2026-11-14); HTML [S-05-evidence.html](../docs/design/screens/S-05-evidence.html) |
| S-06 Script and demonstration | R-11–R-15, R-59, Gate B | SPEC-45 | Approved (canvas, 2026-11-14); HTML [S-06-script.html](../docs/design/screens/S-06-script.html) |
| S-07 Storyboard and preview | R-16, R-18–R-23, R-27, R-28, Gate C | SPEC-51, SPEC-52 | Approved (canvas, 2026-11-14); HTML [S-07-storyboard.html](../docs/design/screens/S-07-storyboard.html) |
| S-08 Narration | R-25, R-26 | SPEC-49 | Approved (canvas, 2026-11-14); HTML [S-08-narration.html](../docs/design/screens/S-08-narration.html) |
| S-09 Revision impact | R-31, R-32, R-42 | SPEC-64 | Approved (canvas, 2026-11-14); HTML [S-09-revision.html](../docs/design/screens/S-09-revision.html) |
| S-10 Compare versions | R-33 | SPEC-65 | Approved (canvas, 2026-11-14); HTML [S-10-compare.html](../docs/design/screens/S-10-compare.html) |
| S-11 Final review and package | R-29, R-30, R-37, R-38, R-45, R-54, R-55, R-60, Gate D | SPEC-57, SPEC-58, SPEC-73 | Approved (canvas, 2026-11-14); HTML [S-11-package.html](../docs/design/screens/S-11-package.html) |
| S-12 Publication record (R2) | R-46–R-49, R-72 (manual), Gate E | SPEC-72 | Approved (canvas, 2026-11-14); HTML [S-12-publication.html](../docs/design/screens/S-12-publication.html) |
| S-13 Runs and recovery | R-50–R-53 | SPEC-40, SPEC-66 | Approved (canvas, 2026-11-14); HTML [S-13-runs.html](../docs/design/screens/S-13-runs.html) |
| S-14 Cost and effort | R-34–R-36 | SPEC-67 | Approved (canvas, 2026-11-14); HTML [S-14-cost.html](../docs/design/screens/S-14-cost.html) |
| S-15 Library | R-02, R-55, R-62 | SPEC-59 | Approved (canvas, 2026-11-14); HTML [S-15-library.html](../docs/design/screens/S-15-library.html) |
| S-16 Series slate (R2) | R-39, R-58 | SPEC-75 | Approved (canvas, 2026-11-14); HTML [S-16-slate.html](../docs/design/screens/S-16-slate.html) |
| S-17 Connections (R3) | R-66, R-67 | — | Planned (prototype after A-18) |
| S-18 Publishing calendar (R3) | R-68–R-71 | — | Planned (prototype after A-18) |
| S-19 Opportunity Lab (R3) | R-73 | — | Planned (prototype after A-18) |
| S-20 Analytics and experiments (R3) | R-72, R-74–R-77 | — | Planned (prototype after A-18) |

Full list and R-xx → screen map: [UI_DESIGN.md](../docs/product/UI_DESIGN.md).

## Requirements baseline

[REQUIREMENTS.md](../docs/product/REQUIREMENTS.md): R-01–R-82, NFR-01–NFR-19, KPI-01–KPI-14, F-01–F-21. Baselined at G1 (2026-11-12, PR #2); changes only through change control.

| G1 check | Result |
|---|---|
| Every PRD section maps to an R-xx / NFR-xx / KPI-xx or is out of scope | Pass with note: §2.4, §6.11, §22–25 and §27 hold no product requirement and are marked "input to" a Stage 2–3 doc |
| Every Must has acceptance criteria | Pass (all Must and Should items have Given/When/Then) |
| Questions answered or assumptions accepted | Pass: Q-03 and Q-07 answered, Q-05 parked with an interim rule, all other assumptions accepted (2026-11-12) |
| Agent steps have a maturity target and a named approver (PROCESS.md, added 2026-11-14) | Pass: Q-33 accepted; table in [AGENT_ARCHITECTURE.md](../docs/architecture/AGENT_ARCHITECTURE.md#maturity-per-workflow); every agent output is a draft approved at S-05, Gate B, Gate C or on S-09 by the owner |

## Design (Stage 2)

| Part | Docs | Status |
|---|---|---|
| 2a | [ARCHITECTURE.md](../docs/architecture/ARCHITECTURE.md), [ADR-001–014](../docs/adr/README.md) (all accepted), [contracts 0.1.0](../docs/contracts/README.md) | Done (PR #3, merged 2026-11-12) |
| 2b | [UI_DESIGN.md](../docs/product/UI_DESIGN.md), [TECH_STACK.md](../docs/architecture/TECH_STACK.md), [SECURITY.md](../docs/architecture/SECURITY.md), [OBSERVABILITY.md](../docs/architecture/OBSERVABILITY.md), ADR-015–019, [contracts 0.2.0](../docs/contracts/README.md#change-log) | Done (PR #4, merged 2026-11-12); decisions taken 2026-11-13 |
| 2c | [tokens.md](../docs/design/tokens.md) (Studio UI tokens, video house style brand kit v1 per A-31), the S-07 reference prototype, S-01–S-16 on the [Claude Design canvas](https://claude.ai/artifact/6jStrLtkcRDG5GfEf5g8HS). Addendum: [AGENT_ARCHITECTURE.md](../docs/architecture/AGENT_ARCHITECTURE.md) (maturity per workflow, journeys → agents, execution contract, AG-UI, conformance scenarios), [ADR-020](../docs/adr/ADR-020-ag-ui-event-stream.md), [ADR-021](../docs/adr/ADR-021-agent-runtime-contract.md), [contracts 0.4.0](../docs/contracts/README.md#change-log) | Canvas approved 2026-11-14; HTML S-01–S-16 in review (PR #7); agent addendum decided (Q-33–Q-35, ADR-020/021 confirmed 2026-11-14) (PR #5) |

| G2 check | Result |
|---|---|
| Traceability: every R-xx maps to a component and every user-facing R-xx to a screen | Pass: all Must and Should R-xx → component (2a) and → screen S-01–S-20 (2b, checked by script: 0 unmapped); R3 screens S-17–S-20 listed, prototyped after A-18; Could and Won't not designed. Every KPI-01–14 has an analytics event. |
| Contracts versioned | Pass: 0.4.0 (revision redraft through the agent, Q-34; approval policy versions, Q-35; 0.3.0 agent execution contract and AG-UI stream before it; change log in contracts README). Re-checked 2026-11-14: 13 schemas pass the 2020-12 metaschema; all `$ref`s in `agui/stream.json`, `execution.schema.json` and `openapi.yaml` resolve; the four example AG-UI streams have ordered cursors and their snapshot, activity and tool-call payloads validate; sample TaskContract and AgentResult validate; DDL applies to PostgreSQL 16 (44 tables). AG-UI event field names are checked against the pinned SDK in the M0 relay spec. |
| Each layer can mock the others | Pass: mocking guide in contracts README; synthetic odd-squares fixtures |
| No open choice blocks M0 | Pass: ADR-011–014 accepted; Remotion free individual licence; development runs on free credits (Q-05). |
| Nothing designed that no requirement asks for | Pass: R3 planned only; R-64, R-65, R-78–R-82 not designed |
| Threat model reviewed | Pass for TH-01–TH-30, agent risks and accepted risks (accepted 2026-11-13, owner delegated to the tech lead). TH-31–TH-34 (AG-UI stream, stale agent results, out-of-scope redrafts) added 2026-11-14, reviewed and accepted with the G2 sign-off (2026-11-14) |
| Agent review checklist (PROCESS.md) | Pass: owners, lifecycle, approval binding (with policy versions, Q-35), schemas, idempotency, reconnect and blocked-state explanation documented in AGENT_ARCHITECTURE.md; maturity per workflow recorded (Q-33); conformance C01–C14 mapped (C08, C13 not applicable) |
| Screens approved | Pass: canvas approved 2026-11-14 (S-01–S-16, journey by journey). HTML prototypes match the canvas: built from the same generators; each switches between sample data and its UI_DESIGN empty, loading and error states; checked headless (78 states, no script errors, no network requests, every link resolves). |
| Every key journey has an SLO | Pass: SLO-01–SLO-10, provisional, calibrate after R0 (A-15) |
| Every layer has a chosen tool | Pass: TECH_STACK.md; exact pins in M0 lockfiles. Q-29 search API still open (does not block M0). |

## Plan (Stage 3)

[DEVELOPMENT_PLAN.md](DEVELOPMENT_PLAN.md) (90 specs SPEC-01a–SPEC-83 after the Stage 4 splits, 192 spec-days, dependency groups, tracks, screen → spec map, Cursor and Claude workflow) · [TEST_STRATEGY.md](TEST_STRATEGY.md) (levels, cadence, eval thresholds, C01–C14 as T-01–T-14, QA-01–QA-12 map, T-01–T-98 catalogue, Definition of Ready and Done, pipeline, environments) · [DELIVERY_PLAN.md](DELIVERY_PLAN.md) (M0–M7, R2 slate, dates, RAID) · [AGENTS.md](../AGENTS.md), [CLAUDE.md](../CLAUDE.md), [.cursor/rules/](../.cursor/rules/) (000-core, backend, agent, media, frontend, contracts, testing, observability) · [ADR-022](../docs/adr/ADR-022-delivery-pipeline-local-hosting.md).

| G3 check | Result |
|---|---|
| Every Must R-xx is in a milestone | Pass (checked by script): all 62 Must R-xx and all 19 NFR-xx map to specs in M0–M7; Should R-66–R-77 are R3 (conditional) except the manual parts of R-48 and R-72; Could and Won't not planned |
| Every spec lists its R-xx and T-xx | Pass: 83 of 83; every T-xx exists in the catalogue (T-13 C13 and T-89 UAT have no spec by design) |
| Every frontend spec lists its approved S-xx | Pass: every W and B+W spec names its screen; S-01–S-16 each built by at least one spec and tested by T-15–T-30 |
| Dependency order valid | Pass: every spec depends only on earlier specs in the same or an earlier milestone |
| You agree what is in each milestone and when | Pass: scope agreed with Q-37–Q-42 accepted; no dates by your decision (Q-36), milestones close on their exit criteria; forecast kept for orientation |

## Open questions and risks

- [QUESTIONS.md](../docs/product/QUESTIONS.md) is the running decision log for Q-01–Q-35 (DEC-01–12 are Q-01–Q-12).
- No open questions. Q-43 accepted 14 Nov 2026 (walking-skeleton diagnostic run and the S-01 System check).
- Q-36 answered 14 Nov 2026: no dates; build it the right way.
- Decided 14 Nov 2026, from [Strategy v1.0](../docs/sources/Strategy-v1.0.md): Q-37–Q-42 accepted (no generative video at R0–R2, no January launch, Remotion only, strategy briefs as M0 candidates, specialist tag for physics What If briefs, secondary manual metrics at R2).
- Risk: several strategy briefs need animation families beyond the six; tagged in M0 and estimated before M6 (DELIVERY_PLAN.md RAID).
- Risk: the plan is about 960 engineering hours (192 spec-days after the M0 splits), roughly 2.6× PRD §22.1's 228–364; the indicative forecast puts go-live around 19 Nov 2027 at 25 h/week (DELIVERY_PLAN.md). Re-estimated after M1.
- Parked: Q-05 budget limits. Development uses free credits with costs recorded; real limits are set from measured per-video cost before the AWS move.
- Before the first real provider call: opt out of ElevenLabs model training on every account; OpenAI calls use `store: false` (SECURITY.md).
- Specialist checks: none outstanding. Q-14, Q-20, Q-25 and the narrator licence rule were decided by the tech lead at your request (engineering decisions, not legal advice).
- Hosting: local only through R2; AWS Mumbai after the R2 gate (Q-21). Staging is a second local environment. Risk: the owner's machine is a single point of failure, so backups are copied off it (NFR-14).
- Narration made on ElevenLabs free credits cannot be published; Gate D blocks it until takes are regenerated on a paid plan (ADR-013).
- Open, low cost: Q-29 search API (SPEC-14).
- Risk: MinIO Community Edition is no longer developed; interim pinned image, replaced by SPEC-05 (ADR-015).
- Risk: DBOS Transact must pass the M0 kill-and-resume spike in SPEC-09b (ADR-003); if it fails, ADR-003 is superseded before M1 depends on it.
- Risk: Remotion render time and memory are unmeasured until the R0 baseline (NFR-02, ADR-002).

## Recent decisions

- 2026-11-14: **SPEC-01a merged** (#13) by the product owner, including the source-built interim object store (ADR-015 amendment line to be added by SPEC-05) and configurable host ports. SPEC-01b, SPEC-02, SPEC-03a, SPEC-05 and SPEC-08 are Ready. Next: SPEC-03a (critical path) and SPEC-02 (CI), within the two-open-specs limit.
- 2026-11-14: **SPEC-01a in review** (PR #13). T-31 passed on your machine: fresh clone → 9 services healthy → `make check` green (8 steps) → `make down` keeps volumes, `CLEAN=1` removes them. Tech lead decisions, for your confirmation: the interim object store is built from MinIO CE's final source tag (`RELEASE.2025-10-15T17-29-55Z`, includes the CVE-2025-62506 fix) on a pinned base, because MinIO withdrew its official images (ADR-015 needs an amendment line); host ports are configurable in `.env`, Keycloak on 8180. Size about 1,700 lines against the spec's 400 (mostly config and tests); not split.
- 2026-11-14: Product owner accepted **Q-43** (A-43: diagnostic run behind `FEATURE_DIAGNOSTICS`, off in production; System check entry in the S-01 app shell as an approved screen change, dev and staging only) and confirmed the **M0 splits and size** (21 specs, 39 spec-days).
- 2026-11-14: **Stage 4, M0 prepared** (PR #12, for your review): [milestone.md](M0/milestone.md) and spec.md plus prompt.md for 21 specs. Tech lead decisions: SPEC-01, SPEC-03, SPEC-09 and SPEC-11 split into lettered parts to meet the Definition of Ready (M0 32 → 39 spec-days; critical path unchanged at 39; indicative forecast moves two weeks at 25 h/week); SPEC-04 creates only M0 tables; SPEC-07 calls the API through a Next.js route handler; SPEC-10 maps AG-UI on read from the outbox; T-98 added. Q-43 raised (walking-skeleton diagnostic run, A-43). DEVELOPMENT_PLAN effort table corrected (its spec counts were wrong). Spec template gains the Agent line and the media layer, as in PROCESS.md.
- 2026-11-14: **G2 and G3 signed** by the product owner. Architecture, agent architecture, UI design, tech stack, security, observability and the approved screens are baselined (change control from here). Development plan, test strategy and delivery plan agreed; ADR-022 confirmed. Next: Stage 4 prepares the M0 specs.
- 2026-11-14: Q-36 answered: no capacity commitment and no milestone dates; milestones close on exit criteria (in line with Q-03). Forecast windows kept as indicative only.
- 2026-11-14: Q-37–Q-42 accepted by the product owner; baseline and dates unchanged.
- 2026-11-14: Strategy v1.0 added as a companion source (`docs/sources/Strategy-v1.0.md`). No requirement added; coverage traced in REQUIREMENTS.md; Q-37–Q-42 raised with assumptions that keep the baseline; DELIVERY_PLAN (M0 tasks, phase map, R2 gate outcomes, RAID), DEVELOPMENT_PLAN (strategy inputs → specs) and TEST_STRATEGY (eval topics, tracked beat timing) updated.

- 2026-11-14: Stage 3 (tech lead, for you to confirm at G3): milestones M0 Foundation → M1 R0 feasibility (media first, PRD §22) → M2–M5 R1 slices → M6 R2 features → M7 hardening → R2 slate; re-estimate and renderer check after M1 (PRD §22.1–22.2). ADR-022: CI verifies, your machine builds each release once, staging and production are local Compose projects promoted by digest. ADR-019 amended (k6, OWASP ZAP, diff-cover). Eval thresholds set (hard gates zero; rates provisional, calibrated at M2 and M3). Conformance C05–C11 due at M2 exit, not M1 (M1 has no approvals, agent runs or budgets). Q-36 raised.

- 2026-11-14: You approved the screens on the Claude Design canvas. HTML prototypes S-01–S-16 built in docs/design/screens/ (S-07 is the step-1 reference prototype).
- 2026-11-14: Q-32 accepted: the four moats stay hypotheses until their PRD §1.1 proof is met (moats 1–3 at the R2 gate, moat 4 at R3); no external defensibility claim before R4 pilots show repeat use.
- 2026-11-14: Product owner: revisions go through the agent (Q-34): the script or storyboard agent redrafts only the targeted beat or scene, impact is shown before any render, hand edits stay available (R-31 AC3). Q-33 maturity targets and Q-35 approval policy versions accepted (delegated to the tech lead; approvals record brand-kit, rubric and content-policy versions; a rubric or policy change reopens Gate D for unpublished packages; scheduled Gate E approvals lapse at their time; R-41 AC3). ADR-020 and ADR-021 confirmed. Contracts 0.4.0. S-09 updated on the canvas.
- 2026-11-14: Agent architecture redone from the Agentic Application Reference Architecture v1.2, its Engineering Practices Guidebook v1.0 and the Agent Capability Maturity Framework (the 2026-11-13 version, built from the wrong source, was reverted). PROCESS.md: generic "Agent architecture" section (golden rules, maturity per workflow, planes, execution contract, harness, validation stages, tools and effects, approvals, AG-UI, conformance C01–C14, ten agent ADRs) wired through stages 1–7. OpportunityOS: AGENT_ARCHITECTURE.md; ADR-020 (AG-UI on the project stream, observe mode, outbox `seq` cursor) and ADR-021 (thin agent runtime, per-attempt contract and context envelope, stale results rejected) accepted by the tech lead, owner confirms at G2; contracts 0.3.0; TH-31–TH-33; Q-33–Q-35 raised. No requirement changed.
- 2026-11-13: Product owner: the PRD may be revised in place during discovery (until G3), with a dated revision note; PRD §1.1 "What the product solves and defensibility" added (problems solved, four moat hypotheses, proof checkpoints). Q-32 raised. PROCESS.md: Stage 1 starts with product framing (personas, journeys, stories, value and moat hypotheses); Stage 2 screens go UI_DESIGN.md → Claude Design canvas by journey → client review on the canvas → HTML in the repo. Figma not used.
- 2026-11-13: S-01–S-16 designed on the Claude Design canvas, one page per journey (J1, J6, J3), plus a journey map and a "What it solves" page.
- 2026-11-13: S-07 slimmed at your request: the Remotion Player's own controls (frame and scene steps in its custom-controls slot), a scene and caption strip instead of a multi-track timeline (PRD §13 defers one); action timing lives in the inspector.
- 2026-11-13: Stage 2c step 1 (tech lead decisions, in your review): Studio typeface and video typeface Atkinson Hyperlegible Next and Mono (SIL OFL 1.1), equations in KaTeX fonts (OFL); five layer colours chosen for colour-blind separation; safe zones as the union of Shorts and Reels overlays, provisional; brand cue is the "Signal Motion" wordmark with a 2 × 2 mark, closure only. Font files go into the rights ledger before first use (R-55).
- 2026-11-13: G2 review items decided (owner delegated to the tech lead): threat model and accepted risks accepted; Q-30 (access audit kept 1 year) and Q-31 (video house style in 2c) accepted; contract gaps closed in contracts 0.2.0 (project delete/archive, KPI baselines, analytics schema, `fetch_source` limited to search results, operator URLs and one-hop links); sessions 12 h idle / 7 days absolute with step-up MFA for Gate E, budget raise, deletion and export; backups 30 dailies plus a pre-migration snapshot; estimates at ₹95/USD, actuals at the recorded rate; breach notices follow DPDP Rule 7.
- 2026-11-13: Stage 2b ADRs accepted by the tech lead: ADR-015 local object store (MinIO CE interim, replaced in M0), ADR-016 OpenTelemetry + Grafana LGTM, ADR-017 KPI events in PostgreSQL, ADR-018 Studio UI kit, ADR-019 toolchain. Q-30, Q-31 raised.

- 2026-11-13: Q-05 dev rule (no limits, free credits, costs recorded); Q-21 AWS after the R2 gate; Q-14, Q-20, Q-25 answered and narrator licence rule set by the tech lead.
- 2026-11-12: Provider decisions: local only now, AWS Mumbai later (ADR-011, Q-21); Keycloak locally, Cognito when hosted (ADR-012, Q-22); ElevenLabs (ADR-013) and OpenAI gpt-5.4-mini-2026-03-17 (ADR-014) (Q-06); Remotion free individual licence (Q-07).
- 2026-11-12: Stage 2a ADRs accepted: ADR-001 modular monolith (backend, agent, media, web), ADR-002 Remotion only, ADR-003 DBOS Transact durable execution via outbox, ADR-004 FastAPI, ADR-005 Next.js, ADR-006 PostgreSQL, ADR-007 S3 storage, ADR-008 Pydantic → JSON Schema → TS, ADR-009 provider adapters, ADR-010 transactional outbox.
- 2026-11-12: G1 Requirements baseline signed by the product owner / tech lead (PR #2).
- 2026-11-12: Q-03: no launch date; build properly through R0 → R1 → R2, without the smaller January launch.
- 2026-11-12: Q-07: Remotion is the only renderer; no Temporal, no Manim. ADRs follow in Stage 2.
- 2026-11-12: Q-05 budget limits parked; costs still recorded and reservation still built.
- 2026-11-12: Stage 1 mapping. PRD P0 = Must, P1 = Should (R3), P2/P3 = Won't; PRD-optional behaviour (chat drafting, model critique, extra animation families) = Could. R4/R5 items kept as Won't R-78–R-82 for traceability.
- 2026-11-12: DISCOVERY.md not created: the PRD involves no existing system.
- 2026-11-12: Repo bootstrapped. PRD v2.0 stored unchanged in docs/sources/.
