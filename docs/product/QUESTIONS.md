# Questions and assumptions

Running log of every open question and decision found in [PRD v2.0](../sources/PRD-v2.0.md), kept for future reference. Requirements live in [REQUIREMENTS.md](REQUIREMENTS.md); this file owns only questions, assumptions and their decisions. A decision that needs a record of its reasoning also gets an ADR in `docs/adr/`.

**How to use it**
- Each question Q-n has one assumption A-n (same number). Work builds on A-n until the question is decided.
- **Status:** Open (not yet reviewed) · Accepted (A-n confirmed as the decision) · Answered (decision differs from A-n) · Parked (deferred; the interim rule shown applies until it is decided).
- Never delete a row. To change a decision, update its row, add a line to the change log and, after G1, follow change control.
- New questions take the next number (Q-29 onward).

**Answerer key:** PO = product owner/client · TL = tech lead · SP = specialist reviewer (legal, privacy, copyright or subject) · PF = platform account preflight (PRD OOS-004). Today one person is PO and TL.

## Questions and decisions

### PRD open decisions (PRD §26)

| Q | Question | Source | Answerer | Status | Decision (or assumption in force) | Follow-up |
|---|---|---|---|---|---|---|
| Q-01 | What is the public channel name and identity? | DEC-01 | PO | Accepted | A-01: Internally the platform is "OpportunityOS" and the engine "Signal Motion". Screens and fixtures use the placeholder channel name "Signal Motion (working name)". | Final identity before the first public upload (R2). |
| Q-02 | Confirm the broad STEM/technology promise and pick the twelve briefs and first three topics. | DEC-02 | PO | Accepted | A-02: Channel promise as in PRD §5. The first story is the odd-numbers square (PRD §10). The other two first topics come from different series and are chosen when the M0 specs are written. | Pick topics in Stage 4 (M0 specs). |
| Q-03 | Is January 2027 a commitment, what weekly capacity is available, and which launch shape? | DEC-03 | PO | Answered | No launch date. Build the product properly through R0 → R1 → R2; the smaller January launch in PRD §22.1 is not used. Capacity is not fixed; milestone dates are proposed at G3 and you agree them. | — |
| Q-04 | Who reviews which claims, which topics need a specialist, and do we adopt the proposed rubric and 10-of-12 reliability threshold? | DEC-04 | PO, SP | Accepted | A-04: You review all claims. Elementary maths and science are self-reviewed with a cited derivation or reference. Health, finance, advanced science and legal claims are marked "needs specialist" and block approval (R-09). Rubric 1–5 with every dimension ≥ 4; reliability threshold 10 of 12. | Calibrate the rubric on the first three videos. |
| Q-05 | What are the monthly ceiling and per-video allowance, in which currency, and do fixed costs and human time count in unit cost? | DEC-05 | PO | Parked | Interim rule: costs are still recorded (R-35, R-36) and budget reservation is still built (R-34), but limits are configuration with no default. Reporting currency INR; provider USD converted at a recorded rate. | Decide limits before the first paid provider call (R0 spike). |
| Q-06 | Which TTS voice, LLM and asset providers? | DEC-06 | TL (needs your approval), SP for narrator licence | Accepted | A-06: Every provider sits behind an adapter (NFR-11). Stage 2 writes Proposed ADRs with two candidates each; nothing is called until you approve. The narrator licence must allow commercial use of the synthetic voice on YouTube and Instagram. | Approve providers in Stage 2. SP confirms narrator licence. |
| Q-07 | Confirm Remotion + FFmpeg (licence eligibility, ref S10–S11), Temporal after a restart/replay spike, and Manim only where needed. | DEC-07 | TL, SP for Remotion licence terms | Answered | Remotion is the only renderer (it uses FFmpeg internally). Manim is not used. Temporal is not used. Durable execution (NFR-01, R-51) is met another way, chosen by ADR in Stage 2, without a custom workflow framework (PRD §14.2). | Stage 2: ADR for Remotion and for durable execution. SP confirms Remotion licence eligibility. |
| Q-08 | Which YouTube account is the destination, what API access and quota does it have, and is an Instagram professional account eligible? | DEC-08 | PO, PF | Accepted | A-08: R2 publishes manually to YouTube only. No adapter before R3. Instagram stays off until eligibility is verified. | Account preflight before R3. |
| Q-09 | Which available attention measure is the primary metric, over what window? | DEC-09 | PO | Accepted | A-09: Average percentage viewed (or the closest supported retention measure) over seven days with a later follow-up, entered manually from YouTube Studio at R2 and labelled cold-start (KPI-06). | — |
| Q-10 | Who is the paying buyer (creator or studio) and at what price? | DEC-10 | PO | Accepted | A-10: Out of this baseline (R4 = Won't). No commercial work. | Revisit before R4. |
| Q-11 | How is the 48-video growth study allocated, and does it start? | DEC-11 | PO | Accepted | A-11: The study does not start without your explicit go after R2. The 4/4/2/2 mix holds until then. | Revisit after R2. |
| Q-12 | Which business vertical, first-party integrations and evidence threshold for R5? | DEC-12 | PO | Accepted | A-12: Out of this baseline (R5 = Won't). | Revisit before R5. |

### Gaps found in the PRD

| Q | Question | Source | Answerer | Status | Decision (or assumption in force) | Follow-up |
|---|---|---|---|---|---|---|
| Q-13 | How is the "documented manual baseline" for effort produced, and how are P01/P02 validated? | §2.4, §19.3, §21.2 | PO | Accepted | A-13: During discovery you time one comparable Short made with your current manual tools; its active time, revisions and cost are the baseline (KPI-04). P01/P02 validation is your own observed sessions, logged in retros. | Do this in M0. |
| Q-14 | How long are superseded drafts, logs, source excerpts and tokens kept? | §15, §20 | PO, SP (privacy) | Accepted | A-14: Anything linked to an approved or published version is kept indefinitely. Unapproved superseded render artifacts are deleted after 90 days; logs after 30 days. No personal data beyond the owner's account. | SP confirms with Q-20. |
| Q-15 | What are the targets for preview time, master render time and Studio responsiveness? | §20 | TL | Accepted | A-15: No numeric targets until the R0 baseline (NFR-02). SLOs are then set in OBSERVABILITY.md through change control. | Set after R0. |
| Q-16 | What recovery point and recovery time apply? | §20; PROCESS operate | TL | Accepted | A-16: RPO 24 hours (daily backup), RTO one working day for this internal tool; restore rehearsed in hardening (NFR-14). | — |
| Q-17 | Which accessibility standard measures contrast, flashing and Studio access? | §5.2, §20 | TL | Accepted | A-17: WCAG 2.2 AA contrast (4.5:1 text, 3:1 large text and graphics) for video text and the Studio; no more than three flashes per second; the Studio is keyboard-usable. | — |
| Q-18 | What exactly triggers starting R3? | §1, §4 | PO | Accepted | A-18: R3 starts only when you sign the R2 gate and explicitly promote it. Until then R3 (Should) items are planned in outline only. | — |
| Q-19 | How is viewer comprehension tested "where possible"? | §2.2, §10.3, §19.1 | PO | Accepted | A-19: Your muted-with-captions review is the R2 check (KPI-14). No viewer study before R3; comments are read qualitatively. | — |
| Q-20 | Which personal-data law applies (India's DPDP Act, or GDPR as well)? | PROCESS §Stage 2; PRD §20 | SP (privacy/legal) | Accepted | A-20: The DPDP Act 2023 applies. The product handles only the owner's account data and aggregate channel analytics, never viewer personal data, so obligations cover the owner account and connection tokens. | SP confirms before G2 (SECURITY.md). |
| Q-21 | Which cloud host runs staging and production? | §14.2; project rules | TL (needs your approval) | Accepted | A-21: Chosen by you in Stage 2. Working assumption: a single-region container host with managed PostgreSQL and S3-compatible storage. | Decide in Stage 2. |
| Q-22 | Which authentication provider? | §20 FR-29; project rules | TL (needs your approval) | Accepted | A-22: One owner account through a managed auth provider with MFA; no self-built password store. Chosen in Stage 2 with your approval. | Decide in Stage 2. |
| Q-23 | Is AI-assisted development (Cursor Composer 2.5, Claude) allowed, and is Cursor privacy mode required? | PROCESS §AI tool hygiene | PO | Accepted | A-23: Allowed, with privacy mode on and synthetic data only in prompts, fixtures and screens. | — |
| Q-24 | Will videos use music, sound effects or generative illustrations? | §5.2, §21.1 | PO | Accepted | A-24: No music and no generative illustrations at R1/R2. Narration only, with optional licensed sound effects registered in the rights ledger (R-55). | — |
| Q-25 | How much source text may be stored as evidence? | §15 | SP (copyright) | Accepted | A-25: Store citation metadata, URL, location and a short excerpt (under 25 words) per claim; never full-page copies. | SP confirms before G2. |
| Q-26 | Which devices and browsers must the Studio support? | §13 | PO | Accepted | A-26: Current desktop Chrome, Safari and Firefox at 1280 px and wider; previews show a phone-size frame. No mobile Studio. | — |
| Q-27 | Should package approval be blocked until the audience (made-for-kids) setting is set explicitly? | §7.1 | PO | Accepted | A-27: Yes. It is set per package with no default (R-04 AC2). | — |
| Q-28 | Are chat-driven drafting (R-64) and model critique in QA (R-65) wanted at R1? | §13, §14.1 | PO | Accepted | A-28: Neither is in R1; reconsider after R1. | Revisit after R1. |

## Still to do

- **Parked:** Q-05 budget limits, before the first paid provider call.
- **Specialist confirmation (assumption in force until then):** Q-06 narrator licence, Q-07 Remotion licence eligibility, Q-14 and Q-20 privacy and DPDP Act, Q-25 stored excerpt length. Due before G2.
- **Your approval in Stage 2:** Q-06 providers, Q-21 cloud host, Q-22 auth provider, and the durable-execution approach that replaces Temporal (Q-07).

## Change log

| Date | Change | By |
|---|---|---|
| 2026-11-12 | Q-01–Q-28 raised in Stage 1. | Claude |
| 2026-11-12 | Q-03 answered (no date; build properly, no smaller launch). Q-05 parked. Q-07 answered (Remotion only; no Temporal, no Manim). All other assumptions accepted. | Product owner |
