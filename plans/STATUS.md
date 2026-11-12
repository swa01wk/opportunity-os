# STATUS: OpportunityOS        Updated: 2026-11-12
Current stage: 1 Intake (no milestone yet) | Next gate: G1 Requirements baseline, awaiting product owner sign-off

Release target: R0 -> R1 -> R2 (PRD Section 4). R3 conditional; R4/R5 out of scope.

## Stages and gates

All gates are signed by the product owner / tech lead (same person).

| Stage | Gate | Status | Signed | PR |
|---|---|---|---|---|
| 0 Bootstrap | — | Done (merged 2026-11-12) | — | chore/bootstrap, #1 |
| 1 Intake | G1 Requirements baseline | In review: 2 of 3 G1 checks pass; open questions need answers or accepted assumptions | | docs/stage-1-intake, #2 |
| 2 Design | G2 Design review and screens | Not started | | |
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

[REQUIREMENTS.md](../docs/product/REQUIREMENTS.md): R-01–R-82, NFR-01–NFR-19, KPI-01–KPI-14, F-01–F-21. Draft for G1.

| G1 check | Result |
|---|---|
| Every PRD section maps to an R-xx / NFR-xx / KPI-xx or is out of scope | Pass with note: §2.4, §6.11, §22–25 and §27 hold no product requirement and are marked "input to" a Stage 2–3 doc |
| Every Must has acceptance criteria | Pass (all Must and Should items have Given/When/Then) |
| Questions answered or assumptions accepted | **Fail**: Q-01–Q-28 open |

## Open questions and risks

- 28 open questions in [QUESTIONS.md](../docs/product/QUESTIONS.md): DEC-01–12 as Q-01–Q-12, plus 16 PRD gaps (Q-13–Q-28).
- Needed for G1: Q-23 (AI-assisted development allowed), Q-27 (explicit made-for-kids setting), and acceptance of the remaining assumptions.
- Specialist review needed: Q-04 (subject scope), Q-06 (narrator licence), Q-07 (Remotion licence), Q-14 and Q-20 (privacy, DPDP Act), Q-25 (copyright of stored excerpts).
- Ask-before choices for Stage 2: cloud host (Q-21), auth (Q-22), Temporal and Remotion licence (Q-07), TTS and LLM providers (Q-06).

## Recent decisions

- 2026-11-12: Stage 1 mapping. PRD P0 = Must, P1 = Should (R3), P2/P3 = Won't; PRD-optional behaviour (chat drafting, model critique, extra animation families) = Could. R4/R5 items kept as Won't R-78–R-82 for traceability.
- 2026-11-12: DISCOVERY.md not created: the PRD involves no existing system.
- 2026-11-12: Repo bootstrapped. PRD v2.0 stored unchanged in docs/sources/.
