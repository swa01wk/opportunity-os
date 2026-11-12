# Questions and assumptions

Running log of every open question and decision found in [PRD v2.0](../sources/PRD-v2.0.md), kept for future reference. Requirements live in [REQUIREMENTS.md](REQUIREMENTS.md); this file owns only questions, assumptions and their decisions. A decision that needs a record of its reasoning also gets an ADR in `docs/adr/`.

**How to use it**
- Each question Q-n has one assumption A-n (same number). Work builds on A-n until the question is decided.
- **Status:** Open (not yet reviewed) · Accepted (A-n confirmed as the decision) · Answered (decision differs from A-n) · Parked (deferred; the interim rule shown applies until it is decided).
- Never delete a row. To change a decision, update its row, add a line to the change log and, after G1, follow change control.
- New questions take the next number (Q-32 onward).

**Answerer key:** PO = product owner/client · TL = tech lead · SP = specialist reviewer (legal, privacy, copyright or subject) · PF = platform account preflight (PRD OOS-004). Today one person is PO and TL.

## Questions and decisions

### PRD open decisions (PRD §26)

| Q | Question | Source | Answerer | Status | Decision (or assumption in force) | Follow-up |
|---|---|---|---|---|---|---|
| Q-01 | What is the public channel name and identity? | DEC-01 | PO | Accepted | A-01: Internally the platform is "OpportunityOS" and the engine "Signal Motion". Screens and fixtures use the placeholder channel name "Signal Motion (working name)". | Final identity before the first public upload (R2). |
| Q-02 | Confirm the broad STEM/technology promise and pick the twelve briefs and first three topics. | DEC-02 | PO | Accepted | A-02: Channel promise as in PRD §5. The first story is the odd-numbers square (PRD §10). The other two first topics come from different series and are chosen when the M0 specs are written. | Pick topics in Stage 4 (M0 specs). |
| Q-03 | Is January 2027 a commitment, what weekly capacity is available, and which launch shape? | DEC-03 | PO | Answered | No launch date. Build the product properly through R0 → R1 → R2; the smaller January launch in PRD §22.1 is not used. Capacity is not fixed; milestone dates are proposed at G3 and you agree them. | — |
| Q-04 | Who reviews which claims, which topics need a specialist, and do we adopt the proposed rubric and 10-of-12 reliability threshold? | DEC-04 | PO, SP | Accepted | A-04: You review all claims. Elementary maths and science are self-reviewed with a cited derivation or reference. Health, finance, advanced science and legal claims are marked "needs specialist" and block approval (R-09). Rubric 1–5 with every dimension ≥ 4; reliability threshold 10 of 12. | Calibrate the rubric on the first three videos. |
| Q-05 | What are the monthly ceiling and per-video allowance, in which currency, and do fixed costs and human time count in unit cost? | DEC-05 | PO | Parked | Dev stage (product owner, 2026-11-13): no budget limits; providers run on free credits. Cost is still recorded per attempt (R-35) and reservation still runs (R-34, NFR-07), against a generous default allowance set in local configuration, so it never blocks development. Per-video cost is estimated from R0/M-milestone runs. Reporting currency INR; provider USD converted at a recorded rate. | Set real limits from the measured per-video cost before the AWS move (Q-21). |
| Q-06 | Which TTS voice, LLM and asset providers? | DEC-06 | TL (needs your approval), SP for narrator licence | Answered | TTS: ElevenLabs (ADR-013). LLM: OpenAI `gpt-5.4-mini`, pinned to `gpt-5.4-mini-2026-03-17` (ADR-014). Both behind adapters (NFR-11). No real call before Q-05 budget limits are set. | Narrator licence rule (tech-lead decision, 2026-11-13): any narration in a published package must be generated on a paid ElevenLabs plan (the free plan has no commercial licence) with a default or library voice licensed for commercial use, or the owner's own voice; never a clone of another person. Plan and commercial-use flag are recorded per take; Gate D is blocked otherwise (R-55). Free credits are fine for development. |
| Q-07 | Confirm Remotion + FFmpeg (licence eligibility, ref S10–S11), Temporal after a restart/replay spike, and Manim only where needed. | DEC-07 | TL, SP for Remotion licence terms | Answered | Remotion is the only renderer (it uses FFmpeg internally). Manim is not used. Temporal is not used. Durable execution: DBOS Transact (ADR-003). Licensee: the owner as an individual, so the free Remotion licence applies (2026-11-12). | ADR-002, ADR-003 written. M0 restart spike confirms ADR-003. Re-check the Remotion licence if ownership moves to a company of more than three people. |
| Q-08 | Which YouTube account is the destination, what API access and quota does it have, and is an Instagram professional account eligible? | DEC-08 | PO, PF | Accepted | A-08: R2 publishes manually to YouTube only. No adapter before R3. Instagram stays off until eligibility is verified. | Account preflight before R3. |
| Q-09 | Which available attention measure is the primary metric, over what window? | DEC-09 | PO | Accepted | A-09: Average percentage viewed (or the closest supported retention measure) over seven days with a later follow-up, entered manually from YouTube Studio at R2 and labelled cold-start (KPI-06). | — |
| Q-10 | Who is the paying buyer (creator or studio) and at what price? | DEC-10 | PO | Accepted | A-10: Out of this baseline (R4 = Won't). No commercial work. | Revisit before R4. |
| Q-11 | How is the 48-video growth study allocated, and does it start? | DEC-11 | PO | Accepted | A-11: The study does not start without your explicit go after R2. The 4/4/2/2 mix holds until then. | Revisit after R2. |
| Q-12 | Which business vertical, first-party integrations and evidence threshold for R5? | DEC-12 | PO | Accepted | A-12: Out of this baseline (R5 = Won't). | Revisit before R5. |

### Gaps found in the PRD

| Q | Question | Source | Answerer | Status | Decision (or assumption in force) | Follow-up |
|---|---|---|---|---|---|---|
| Q-13 | How is the "documented manual baseline" for effort produced, and how are P01/P02 validated? | §2.4, §19.3, §21.2 | PO | Accepted | A-13: During discovery you time one comparable Short made with your current manual tools; its active time, revisions and cost are the baseline (KPI-04). P01/P02 validation is your own observed sessions, logged in retros. | Do this in M0. |
| Q-14 | How long are superseded drafts, logs, source excerpts and tokens kept? | §15, §20 | PO, SP (privacy) | Answered | Tech-lead decision (2026-11-13), A-14 confirmed: anything linked to an approved or published version is kept indefinitely; unapproved superseded render artifacts deleted after 90 days; logs and delivered outbox events after 30 days; fetched source text is never stored (Q-25). This is purpose-based retention with automated deletion, as the DPDP Rules require from 13 May 2027. | Recorded in SECURITY.md (Stage 2b). |
| Q-15 | What are the targets for preview time, master render time and Studio responsiveness? | §20 | TL | Accepted | A-15: No numeric targets until the R0 baseline (NFR-02). SLOs are then set in OBSERVABILITY.md through change control. | Set after R0. |
| Q-16 | What recovery point and recovery time apply? | §20; PROCESS operate | TL | Accepted | A-16: RPO 24 hours (daily backup), RTO one working day for this internal tool; restore rehearsed in hardening (NFR-14). | — |
| Q-17 | Which accessibility standard measures contrast, flashing and Studio access? | §5.2, §20 | TL | Accepted | A-17: WCAG 2.2 AA contrast (4.5:1 text, 3:1 large text and graphics) for video text and the Studio; no more than three flashes per second; the Studio is keyboard-usable. | — |
| Q-18 | What exactly triggers starting R3? | §1, §4 | PO | Accepted | A-18: R3 starts only when you sign the R2 gate and explicitly promote it. Until then R3 (Should) items are planned in outline only. | — |
| Q-19 | How is viewer comprehension tested "where possible"? | §2.2, §10.3, §19.1 | PO | Accepted | A-19: Your muted-with-captions review is the R2 check (KPI-14). No viewer study before R3; comments are read qualitatively. | — |
| Q-20 | Which personal-data law applies (India's DPDP Act, or GDPR as well)? | PROCESS §Stage 2; PRD §20 | SP (privacy/legal) | Answered | Tech-lead decision (2026-11-13): treat the DPDP Act 2023 and DPDP Rules 2025 as applying (a business channel is not purely personal use). Personal data is limited to the owner account (name, email, identity-provider subject) and, from R3, connection tokens. No viewer personal data: analytics are aggregate only and comments are read in the platform, never stored. Safeguards: encryption at rest for credentials (NFR-06), access audit, breach response in RUNBOOK. GDPR not applicable (no EU data subjects targeted). | Recorded in SECURITY.md (Stage 2b). Re-check if viewer data is ever stored or the product serves other workspaces (R4). |
| Q-21 | Which cloud host runs staging and production? | §14.2; project rules | TL (needs your approval) | Answered | Local only (Docker Compose on the owner's machine) until the product objective is met, read as the R2 gate: the 12-video validation slate approved and published (KPI-01). Then AWS Mumbai (ap-south-1) (ADR-011). R1 and R2 are accepted on the local environment; a second local Compose environment with its own credentials serves as staging (NFR-13). | Owner decision 2026-11-13. AWS move is planned after the R2 gate in DELIVERY_PLAN.md (Stage 3). |
| Q-22 | Which authentication provider? | §20 FR-29; project rules | TL (needs your approval) | Answered | Keycloak (OIDC, TOTP MFA) in Docker Compose locally; Amazon Cognito when hosted on AWS (ADR-012). No self-built password store. | Move the owner to Cognito in the AWS migration spec. |
| Q-23 | Is AI-assisted development (Cursor Composer 2.5, Claude) allowed, and is Cursor privacy mode required? | PROCESS §AI tool hygiene | PO | Accepted | A-23: Allowed, with privacy mode on and synthetic data only in prompts, fixtures and screens. | — |
| Q-24 | Will videos use music, sound effects or generative illustrations? | §5.2, §21.1 | PO | Accepted | A-24: No music and no generative illustrations at R1/R2. Narration only, with optional licensed sound effects registered in the rights ledger (R-55). | — |
| Q-25 | How much source text may be stored as evidence? | §15 | SP (copyright) | Answered | Tech-lead decision (2026-11-13), A-25 confirmed: per claim, store citation metadata, URL, retrieval time, locator, content hash and an excerpt under 25 words with attribution; never full-page copies. Fetched text lives only in the running task. Citation validation (R-08 AC2) runs at fetch time; re-checking a citation re-fetches the source. | — |
| Q-26 | Which devices and browsers must the Studio support? | §13 | PO | Accepted | A-26: Current desktop Chrome, Safari and Firefox at 1280 px and wider; previews show a phone-size frame. No mobile Studio. | — |
| Q-27 | Should package approval be blocked until the audience (made-for-kids) setting is set explicitly? | §7.1 | PO | Accepted | A-27: Yes. It is set per package with no default (R-04 AC2). | — |
| Q-28 | Are chat-driven drafting (R-64) and model critique in QA (R-65) wanted at R1? | §13, §14.1 | PO | Accepted | A-28: Neither is in R1; reconsider after R1. | Revisit after R1. |
| Q-29 | Which web search API backs the research task's `search_sources` tool? | §14.1, R-08; found in Stage 2a | TL | Open | A-29: A search API behind a `SearchProvider` adapter (ADR-009), chosen by the M0 research spec on result quality, terms and cost. Model-provider built-in search is not used (ADR-014). Until then the operator supplies source URLs (`operatorSourceUrls`). | Decide in the M0 research spec. |
| Q-30 | Does the 30-day log retention (Q-14) also cover access-audit records, given DPDP Rule 6 asks for logs of access to personal data to be kept for one year? | §20; found in Stage 2b | PO, SP (privacy) | Open | A-30: No. Operational logs, traces and delivered outbox events keep 30 days; access-audit records (`audit_log`, Keycloak login and admin events) are kept 1 year. | Confirm at G2. SECURITY.md applies A-30. |
| Q-31 | Where is the video house style (R-23: palette, type scale, equation typography, caption placement, safe zones, transitions, brand cue) designed? | §5.2, §10; found in Stage 2b | PO | Open | A-31: In Stage 2c, as a separate "video house style" section of `docs/design/tokens.md` (brand kit v1), next to the Studio UI tokens, so S-07 and S-11 prototypes show original video frames. Motion and voice references (PRD OOS-003) follow in M0. | Confirm before 2c. |

## Still to do

- **Parked:** Q-05 budget limits; development runs on free credits with costs recorded. Real limits are set before the AWS move.
- **Specialist checks:** none outstanding. Q-14, Q-20, Q-25 and the narrator licence rule (Q-06) were decided by the tech lead on 2026-11-13 at the owner's request; these are engineering decisions, not legal advice.
- **Open, low cost:** Q-29 search API, decided in the M0 research spec.
- **Open, for G2 / 2c:** Q-30 access-audit retention; Q-31 where the video house style is designed.

## Change log

| Date | Change | By |
|---|---|---|
| 2026-11-12 | Q-01–Q-28 raised in Stage 1. | Claude |
| 2026-11-12 | Q-03 answered (no date; build properly, no smaller launch). Q-05 parked. Q-07 answered (Remotion only; no Temporal, no Manim). All other assumptions accepted. | Product owner |
| 2026-11-12 | Stage 2a: follow-ups for Q-06, Q-07, Q-21, Q-22 point to ADR-002/003/011–014. Q-29 (search API) raised. Requirements unchanged. | Claude |
| 2026-11-12 | Q-06 answered (ElevenLabs; gpt-5.4-mini). Q-07 licensee: individual, free licence. Q-21 answered (local now, AWS Mumbai later). Q-22 answered (Keycloak locally, Cognito when hosted). | Product owner |
| 2026-11-13 | Q-05 interim rule: no limits in development, free credits, cost recorded. Q-21: AWS after the R2 gate. Q-14, Q-20, Q-25 answered and Q-06 narrator licence rule set by the tech lead at the owner's request. | Product owner, Claude |
| 2026-11-13 | Stage 2b: Q-30 (access-audit retention vs DPDP Rule 6) and Q-31 (video house style in 2c) raised. Q-14 and Q-20 recorded in SECURITY.md. Requirements unchanged. | Claude |
