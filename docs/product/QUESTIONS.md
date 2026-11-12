# Questions and assumptions

Gaps and open decisions found in [PRD v2.0](../sources/PRD-v2.0.md) during Stage 1. Each question Q-n has one assumption A-n (same number) that the work builds on until it is answered. Requirements live in [REQUIREMENTS.md](REQUIREMENTS.md); this file owns only the questions and assumptions.

Status: **Open** for G1. At G1 each question is either answered (moved to Resolved) or its assumption is accepted.

**Answerer key:** PO = you as product owner/client · TL = you as tech lead (Stage 2 ADR; several need your explicit approval) · SP = specialist reviewer you name (legal, privacy, copyright or subject) · PF = platform account preflight (PRD OOS-004).

**Needed by:** the latest point an answer is needed before the assumption starts to cost rework.

## Open questions (Q-xx) and assumptions (A-xx)

### PRD open decisions (PRD §26)

| Q | Question | Source | Answerer | Needed by | Assumption we build on |
|---|---|---|---|---|---|
| Q-01 | What is the public channel name and identity? | DEC-01 | PO | Before first public upload (R2) | A-01: Internally the platform is "OpportunityOS" and the engine "Signal Motion". Screens and fixtures use the placeholder channel name "Signal Motion (working name)". |
| Q-02 | Confirm the broad STEM/technology promise and pick the twelve briefs and first three topics. | DEC-02 | PO | PRD M0 discovery (first delivery milestone) | A-02: Channel promise as in PRD §5. The first story is the odd-numbers square (PRD §10). The other two first topics come from different series and are chosen when the M0 specs are written. |
| Q-03 | Is January 2027 a commitment, what weekly capacity is available, and which launch shape? | DEC-03 | PO | G3 | A-03: No date is committed. Plan for the smaller launch in PRD §22.1 (three to five originals, manual uploads, manual analytics) on the way to R1/R2, at 20 hours per week for planning. |
| Q-04 | Who reviews which claims, which topics need a specialist, and do we adopt the proposed rubric and 10-of-12 reliability threshold? | DEC-04 | PO, SP | Rubric: M0 discovery. Reliability: before R2 judging | A-04: You review all claims. Elementary maths and science are self-reviewed with a cited derivation or reference. Health, finance, advanced science and legal claims are marked "needs specialist" and block approval (R-09). Adopt the 1–5 rubric with every dimension ≥ 4 and the 10-of-12 threshold, then calibrate on the first three videos. |
| Q-05 | What are the monthly ceiling and per-video allowance, in which currency, and do fixed costs and human time count in unit cost? | DEC-05 | PO | Before any paid provider call (R0 spike) | A-05: INR is the reporting currency; provider USD costs are converted at a recorded rate. Ceiling and allowance are configuration with no default, so dispatch is blocked until you set them. Fixed costs and human minutes are reported separately (R-35, R-36). |
| Q-06 | Which TTS voice, LLM and asset providers? | DEC-06 | TL (needs your approval), SP for narrator licence | PRD M1 spike | A-06: Every provider sits behind an adapter (NFR-11). Stage 2 writes Proposed ADRs with two candidates each; nothing is called until you approve. The narrator licence must allow commercial use of the synthetic voice on YouTube and Instagram. |
| Q-07 | Confirm Remotion + FFmpeg (licence eligibility, ref S10–S11), Temporal after a restart/replay spike, and Manim only where needed. | DEC-07 | TL (needs your approval), SP for Remotion licence terms | Stage 2 ADRs; confirmed after PRD M1/M2 spikes | A-07: Proposed ADRs for Remotion + FFmpeg and Temporal in Stage 2, confirmed only after the spikes. Remotion eligibility is checked for the actual licensing entity before code depends on it. Manim is not used unless a selected brief needs it. |
| Q-08 | Which YouTube account is the destination, what API access and quota does it have, and is an Instagram professional account eligible? | DEC-08 | PO, PF | Before enabling each adapter (R3) | A-08: R2 publishes manually to YouTube only. No adapter before R3. Instagram stays off until eligibility is verified. |
| Q-09 | Which available attention measure is the primary metric, over what window? | DEC-09 | PO | Before the first measured publication (R2) | A-09: Average percentage viewed (or the closest supported retention measure) over seven days with a later follow-up, entered manually from YouTube Studio at R2 and labelled cold-start (KPI-06). |
| Q-10 | Who is the paying buyer (creator or studio) and at what price? | DEC-10 | PO | Before R4 | A-10: Out of this baseline (R4 = Won't). No commercial work. |
| Q-11 | How is the 48-video growth study allocated, and does it start? | DEC-11 | PO | After the R2 gate | A-11: The study does not start without your explicit go after R2. The 4/4/2/2 mix holds until then. |
| Q-12 | Which business vertical, first-party integrations and evidence threshold for R5? | DEC-12 | PO | Before R5 | A-12: Out of this baseline (R5 = Won't). |

### Gaps found in the PRD

| Q | Question | Source | Answerer | Needed by | Assumption we build on |
|---|---|---|---|---|---|
| Q-13 | How is the "documented manual baseline" for effort produced, and how are P01/P02 validated? | §2.4, §19.3, §21.2 | PO | M0 discovery | A-13: During discovery you time one comparable Short made with your current manual tools; its active time, revisions and cost are the baseline (KPI-04). P01/P02 validation is your own observed sessions, logged in retros. |
| Q-14 | How long are superseded drafts, logs, source excerpts and tokens kept? | §15, §20 | PO, SP (privacy) | G2 (SECURITY.md) | A-14: Anything linked to an approved or published version is kept indefinitely. Unapproved superseded render artifacts are deleted after 90 days; logs after 30 days. No personal data beyond the owner's account. |
| Q-15 | What are the targets for preview time, master render time and Studio responsiveness? | §20 | TL | After the R0 sample | A-15: No numeric targets until the R0 baseline (NFR-02). SLOs are then set in OBSERVABILITY.md through change control. |
| Q-16 | What recovery point and recovery time apply? | §20; PROCESS operate | TL | G2 | A-16: RPO 24 hours (daily backup), RTO one working day for this internal tool; restore rehearsed in hardening (NFR-14). |
| Q-17 | Which accessibility standard measures contrast, flashing and Studio access? | §5.2, §20 | TL | G2 | A-17: WCAG 2.2 AA contrast (4.5:1 text, 3:1 large text and graphics) for video text and the Studio; no more than three flashes per second; the Studio is keyboard-usable. |
| Q-18 | What exactly triggers starting R3? | §1, §4 | PO | After the R2 gate | A-18: R3 starts only when you sign the R2 gate and explicitly promote it. Until then R3 (Should) items are planned in outline only. |
| Q-19 | How is viewer comprehension tested "where possible"? | §2.2, §10.3, §19.1 | PO | Before R2 judging | A-19: Your muted-with-captions review is the R2 check (KPI-14). No viewer study before R3; comments are read qualitatively. |
| Q-20 | Which personal-data law applies (India's DPDP Act, or GDPR as well)? | PROCESS §Stage 2; PRD §20 | SP (privacy/legal) | G2 (SECURITY.md) | A-20: The DPDP Act 2023 applies. The product handles only the owner's account data and aggregate channel analytics, never viewer personal data, so obligations cover the owner account and connection tokens. **Needs a specialist to confirm.** |
| Q-21 | Which cloud host runs staging and production? | §14.2; project rules | TL (needs your approval) | Stage 2 ADR | A-21: No choice made. Working assumption: a single-region container host with managed PostgreSQL and S3-compatible storage. |
| Q-22 | Which authentication provider? | §20 FR-29; project rules | TL (needs your approval) | Stage 2 ADR | A-22: One owner account through a managed auth provider with MFA; no self-built password store. Chosen in Stage 2 with your approval. |
| Q-23 | Is AI-assisted development (Cursor Composer 2.5, Claude) allowed, and is Cursor privacy mode required? | PROCESS §AI tool hygiene | PO | G1 | A-23: Allowed, with privacy mode on and synthetic data only in prompts, fixtures and screens. |
| Q-24 | Will videos use music, sound effects or generative illustrations? | §5.2, §21.1 | PO | Stage 2 | A-24: No music and no generative illustrations at R1/R2. Narration only, with optional licensed sound effects registered in the rights ledger (R-55). |
| Q-25 | How much source text may be stored as evidence? | §15 | SP (copyright) | Stage 2 | A-25: Store citation metadata, URL, location and a short excerpt (under 25 words) per claim; never full-page copies. **Needs a specialist to confirm.** |
| Q-26 | Which devices and browsers must the Studio support? | §13 | PO | G2 | A-26: Current desktop Chrome, Safari and Firefox at 1280 px and wider; previews show a phone-size frame. No mobile Studio. |
| Q-27 | Should package approval be blocked until the audience (made-for-kids) setting is set explicitly? | §7.1 | PO | G1 | A-27: Yes. It is set per package with no default (R-04 AC2). |
| Q-28 | Are chat-driven drafting (R-64) and model critique in QA (R-65) wanted at R1? | §13, §14.1 | PO | G3 | A-28: Neither is in R1; reconsider after R1. |

## By answerer

- **You as product owner:** Q-01, Q-02, Q-03, Q-04, Q-05, Q-09, Q-10, Q-11, Q-12, Q-13, Q-18, Q-19, Q-23, Q-24, Q-26, Q-27, Q-28.
- **You as tech lead (Stage 2 ADRs):** Q-15, Q-16, Q-17; and with explicit approval Q-06, Q-07, Q-21, Q-22.
- **Specialist reviewer:** Q-04 (subject scope), Q-06 (narrator licence), Q-07 (Remotion licence), Q-14 and Q-20 (privacy), Q-25 (copyright).
- **Platform preflight:** Q-08.

## Resolved

None yet.
