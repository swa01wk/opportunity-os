# STATUS: OpportunityOS        Updated: 2026-11-12
Current stage: 2 Design (2a architecture, ADRs, contracts) | Next gate: G2 Design review and screens

Release target: R0 -> R1 -> R2 (PRD Section 4). R3 conditional; R4/R5 out of scope.

## Stages and gates

All gates are signed by the product owner / tech lead (same person).

| Stage | Gate | Status | Signed | PR |
|---|---|---|---|---|
| 0 Bootstrap | — | Done (merged 2026-11-12) | — | chore/bootstrap, #1 |
| 1 Intake | G1 Requirements baseline | Signed | 2026-11-12 | docs/stage-1-intake, #2 |
| 2 Design | G2 Design review and screens | 2a in review (architecture, ADRs, contracts); 2b and 2c not started | | docs/stage-2a-architecture, #3 |
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
| 2a | [ARCHITECTURE.md](../docs/architecture/ARCHITECTURE.md), [ADR-001–014](../docs/adr/README.md) (all accepted), [contracts 0.1.0](../docs/contracts/README.md) | In review |
| 2b | UI_DESIGN.md, TECH_STACK.md, SECURITY.md, OBSERVABILITY.md | Not started |
| 2c | Screens S-xx, tokens.md | Not started |

| G2 check (2a scope) | Result |
|---|---|
| Traceability: every R-xx maps to a component | Pass: all Must and Should R-xx mapped (R3 as planned components); Could and Won't marked not designed. R-xx → screen is 2b. |
| Contracts versioned | Pass: 0.1.0 (`x-version`, in-document versions, OpenAPI `info.version`). Checked: 10 schemas pass the 2020-12 metaschema; valid fixtures pass; 6 schema-level invalid fixtures rejected; 4 semantic fixtures give the expected compiler codes; all OpenAPI `$ref`s resolve; DDL applies to PostgreSQL 16; all 7 diagrams render. |
| Each layer can mock the others | Pass: mocking guide in contracts README; synthetic odd-squares fixtures |
| No open choice blocks M0 | Pass: ADR-011–014 accepted 2026-11-12; Remotion free individual licence. First paid call still needs Q-05 limits. |
| Nothing designed that no requirement asks for | Pass: R3 planned only; R-64, R-65, R-78–R-82 not designed |
| Threat model reviewed | Not in 2a: SECURITY.md (2b) |
| Screens approved | Not in 2a: Stage 2c |

## Open questions and risks

- [QUESTIONS.md](../docs/product/QUESTIONS.md) is the running decision log for Q-01–Q-29 (DEC-01–12 are Q-01–Q-12).
- Parked: Q-05 budget limits, due before the first paid provider call.
- Specialist confirmation due before G2: Q-14 and Q-20 privacy and DPDP Act, Q-25 stored excerpt length. Before the first public upload: Q-06 narrator licence.
- Q-05 budget limits now block the first ElevenLabs or OpenAI call (R0 spike).
- Planning item for G3: when AWS is provisioned; R1 is a hosted release, so before R1 acceptance. Until then the hosted parts of NFR-13, NFR-14 and NFR-15 cannot be verified.
- Open, low cost: Q-29 search API (M0 research spec).
- Risk: DBOS Transact must pass an M0 kill-and-resume spike (ADR-003); if it fails, ADR-003 is superseded before M1 depends on it.
- Risk: Remotion render time and memory are unmeasured until the R0 baseline (NFR-02, ADR-002).

## Recent decisions

- 2026-11-12: Provider decisions: local only now, AWS Mumbai later (ADR-011, Q-21); Keycloak locally, Cognito when hosted (ADR-012, Q-22); ElevenLabs (ADR-013) and OpenAI gpt-5.4-mini-2026-03-17 (ADR-014) (Q-06); Remotion free individual licence (Q-07).
- 2026-11-12: Stage 2a ADRs accepted: ADR-001 modular monolith (backend, agent, media, web), ADR-002 Remotion only, ADR-003 DBOS Transact durable execution via outbox, ADR-004 FastAPI, ADR-005 Next.js, ADR-006 PostgreSQL, ADR-007 S3 storage, ADR-008 Pydantic → JSON Schema → TS, ADR-009 provider adapters, ADR-010 transactional outbox.
- 2026-11-12: G1 Requirements baseline signed by the product owner / tech lead (PR #2).
- 2026-11-12: Q-03: no launch date; build properly through R0 → R1 → R2, without the smaller January launch.
- 2026-11-12: Q-07: Remotion is the only renderer; no Temporal, no Manim. ADRs follow in Stage 2.
- 2026-11-12: Q-05 budget limits parked; costs still recorded and reservation still built.
- 2026-11-12: Stage 1 mapping. PRD P0 = Must, P1 = Should (R3), P2/P3 = Won't; PRD-optional behaviour (chat drafting, model critique, extra animation families) = Could. R4/R5 items kept as Won't R-78–R-82 for traceability.
- 2026-11-12: DISCOVERY.md not created: the PRD involves no existing system.
- 2026-11-12: Repo bootstrapped. PRD v2.0 stored unchanged in docs/sources/.
