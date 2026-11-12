# STATUS: OpportunityOS        Updated: 2026-11-13
Current stage: 2 Design (2b UI, tech stack, security, observability) | Next gate: G2 Design review and screens

Release target: R0 -> R1 -> R2 (PRD Section 4). R3 conditional; R4/R5 out of scope.

## Stages and gates

All gates are signed by the product owner / tech lead (same person).

| Stage | Gate | Status | Signed | PR |
|---|---|---|---|---|
| 0 Bootstrap | — | Done (merged 2026-11-12) | — | chore/bootstrap, #1 |
| 1 Intake | G1 Requirements baseline | Signed | 2026-11-12 | docs/stage-1-intake, #2 |
| 2 Design | G2 Design review and screens | 2a Done (merged 2026-11-12); 2b in review; 2c not started | | docs/stage-2a-architecture, #3 · docs/stage-2b-design, #4 |
| 3 Plan | G3 Milestone scope and dates | Not started | | |

| Milestone | Scope | Status | Exit date |
|---|---|---|---|
| — | Defined in Stage 3 (DELIVERY_PLAN.md) | — | — |

## Current milestone specs
| Spec | Requirements | Screens | Branch / PR | Status | Owner |
|---|---|---|---|---|---|

## Screens
| Screen | Requirements | Specs | Status |
|---|---|---|---|
| S-01 Sign-in and app shell | R-01, R-05 | — | Draft (prototype in 2c) |
| S-02 Projects | R-01, R-44 | — | Draft (prototype in 2c) |
| S-03 Brief and preflight | R-06, R-07, R-57, Gate A | — | Draft (prototype in 2c) |
| S-04 Project settings and data | R-02–R-04, R-34, R-56, R-60 | — | Draft (prototype in 2c) |
| S-05 Evidence | R-08–R-10 | — | Draft (prototype in 2c) |
| S-06 Script and demonstration | R-11–R-15, R-59, Gate B | — | Draft (prototype in 2c) |
| S-07 Storyboard and preview | R-16, R-18–R-23, R-27, R-28, Gate C | — | Draft (prototype in 2c) |
| S-08 Narration | R-25, R-26 | — | Draft (prototype in 2c) |
| S-09 Revision impact | R-31, R-32, R-42 | — | Draft (prototype in 2c) |
| S-10 Compare versions | R-33 | — | Draft (prototype in 2c) |
| S-11 Final review and package | R-29, R-30, R-37, R-38, R-45, R-54, R-55, R-60, Gate D | — | Draft (prototype in 2c) |
| S-12 Publication record (R2) | R-46–R-49, R-72 (manual), Gate E | — | Draft (prototype in 2c) |
| S-13 Runs and recovery | R-50–R-53 | — | Draft (prototype in 2c) |
| S-14 Cost and effort | R-34–R-36 | — | Draft (prototype in 2c) |
| S-15 Library | R-02, R-55, R-62 | — | Draft (prototype in 2c) |
| S-16 Series slate (R2) | R-39, R-58 | — | Draft (prototype in 2c) |
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

## Design (Stage 2)

| Part | Docs | Status |
|---|---|---|
| 2a | [ARCHITECTURE.md](../docs/architecture/ARCHITECTURE.md), [ADR-001–014](../docs/adr/README.md) (all accepted), [contracts 0.1.0](../docs/contracts/README.md) | Done (PR #3, merged 2026-11-12) |
| 2b | [UI_DESIGN.md](../docs/product/UI_DESIGN.md), [TECH_STACK.md](../docs/architecture/TECH_STACK.md), [SECURITY.md](../docs/architecture/SECURITY.md), [OBSERVABILITY.md](../docs/architecture/OBSERVABILITY.md), ADR-015–019, [contracts 0.2.0](../docs/contracts/README.md#change-log) | In review (PR #4); decisions taken 2026-11-13 |
| 2c | Screens S-01–S-16 (R1/R2), tokens.md: Studio UI tokens and, per A-31, the video house style | Not started |

| G2 check (2a + 2b scope) | Result |
|---|---|
| Traceability: every R-xx maps to a component and every user-facing R-xx to a screen | Pass: all Must and Should R-xx → component (2a) and → screen S-01–S-20 (2b, checked by script: 0 unmapped); R3 screens S-17–S-20 listed, prototyped after A-18; Could and Won't not designed. Every KPI-01–14 has an analytics event. |
| Contracts versioned | Pass: 0.2.0 (additive, change log in contracts README). Re-checked 2026-11-13: 11 schemas pass the 2020-12 metaschema; 5 valid fixtures pass; 6 schema-level invalid fixtures rejected; all OpenAPI `$ref`s resolve; DDL applies to PostgreSQL 16 (44 tables). |
| Each layer can mock the others | Pass: mocking guide in contracts README; synthetic odd-squares fixtures |
| No open choice blocks M0 | Pass: ADR-011–014 accepted; Remotion free individual licence; development runs on free credits (Q-05). |
| Nothing designed that no requirement asks for | Pass: R3 planned only; R-64, R-65, R-78–R-82 not designed |
| Threat model reviewed | Pass: STRIDE TH-01–TH-30, agent risks and accepted risks reviewed and accepted 2026-11-13 (owner delegated to the tech lead) |
| Screens approved | Not yet: Stage 2c |
| Every key journey has an SLO | Pass: SLO-01–SLO-10, provisional, calibrate after R0 (A-15) |
| Every layer has a chosen tool | Pass: TECH_STACK.md; exact pins in M0 lockfiles. Q-29 search API still open (does not block M0). |

## Open questions and risks

- [QUESTIONS.md](../docs/product/QUESTIONS.md) is the running decision log for Q-01–Q-29 (DEC-01–12 are Q-01–Q-12).
- Parked: Q-05 budget limits. Development uses free credits with costs recorded; real limits are set from measured per-video cost before the AWS move.
- Before the first real provider call: opt out of ElevenLabs model training on every account; OpenAI calls use `store: false` (SECURITY.md).
- Specialist checks: none outstanding. Q-14, Q-20, Q-25 and the narrator licence rule were decided by the tech lead at your request (engineering decisions, not legal advice).
- Hosting: local only through R2; AWS Mumbai after the R2 gate (Q-21). Staging is a second local environment. Risk: the owner's machine is a single point of failure, so backups are copied off it (NFR-14).
- Narration made on ElevenLabs free credits cannot be published; Gate D blocks it until takes are regenerated on a paid plan (ADR-013).
- Open, low cost: Q-29 search API (M0 research spec).
- Risk: MinIO Community Edition is no longer developed; interim pinned image, replaced in M0 (ADR-015).
- Risk: DBOS Transact must pass an M0 kill-and-resume spike (ADR-003); if it fails, ADR-003 is superseded before M1 depends on it.
- Risk: Remotion render time and memory are unmeasured until the R0 baseline (NFR-02, ADR-002).

## Recent decisions

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
