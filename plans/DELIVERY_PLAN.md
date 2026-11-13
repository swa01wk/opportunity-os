# Delivery plan

Status: **Draft for G3** (Stage 3, 14 Nov 2026). Agreed at G3, then living: dates are re-baselined at M1 exit and whenever change control moves scope. Client view of the plan. The specs behind each milestone are in [DEVELOPMENT_PLAN.md](DEVELOPMENT_PLAN.md); test cadence and exit checks in [TEST_STRATEGY.md](TEST_STRATEGY.md); progress in [STATUS.md](STATUS.md).

Scope is R0 → R1 → R2 (PRD §4). R3 is planned in outline and starts only after you sign the R2 gate and promote it (A-18). R4/R5 are out of scope. Milestones M0–M7 here are PROCESS.md milestones; the PRD's own are written "PRD M0–M6".

## Milestones

Every milestone is a vertical slice you can use end to end, closed by Gate G4 (PROCESS.md exit checklist plus the criteria below). Windows are **proposals** at the capacity in A-36 (Q-36, open); see [Dates, demos and UAT](#dates-demos-and-uat).

| Milestone | Release | At the end you can… | Accepted here | Screens built | Proposed window |
|---|---|---|---|---|---|
| **M0 Foundation** | — | Sign in to an empty Studio and press a button whose run goes web → api → worker → agent (fake) → render → back to the Studio, traced, on a stack any fresh clone brings up | NFR-09, NFR-19 | S-01 (shell) | 23 Nov 2026 – 22 Jan 2027 |
| **M1 Feasibility** | **R0** | Produce the narrated odd-squares sample from a command, with captions, verified values and a targeted revision that reuses unchanged scenes | NFR-03, NFR-11, NFR-12, NFR-16 | — | 25 Jan 2027 – 12 Mar 2027 |
| **M2 Brief to evidence** | R1 | Create a project, set destination, brand, narrator and allowance, write a brief, pass preflight, approve Gate A, run research and review every claim in the Studio | R-01, R-05, R-06, R-08, R-10, R-43, R-50, R-61, NFR-05, NFR-07 | S-01 frame, S-02, S-03, S-04, S-05, S-13 (inspect, cancel) | 15 Mar 2027 – 7 May 2027 |
| **M3 Script to preview** | R1 | Get a script from reviewed claims and approve Gate B, a storyboard checked by the compiler and approve Gate C, audition narration, and watch a draft preview | R-03, R-07, R-11, R-12, R-13, R-14, R-15, R-16, R-17, R-18, R-19, R-20, R-21, R-23, R-25, R-26, R-27, R-28, R-57, NFR-17 | S-06, S-07, S-08 | 10 May 2027 – 25 Jun 2027 |
| **M4 Master to export** | R1 | Render the master, review QA, findings and the rubric, approve Gate D and download an export bundle marked "awaiting manual upload" | R-02, R-04, R-09, R-29, R-30, R-37, R-38, R-44, R-45, R-54, R-55, R-59, R-62 | S-11, S-15 | 28 Jun 2027 – 30 Jul 2027 |
| **M5 Revision and recovery** | **R1 gate** | Ask for a change in words and have the agent redraft only that part, see its impact before any render, apply it, compare versions, recover failed runs, see cost and effort, export or delete project data | R-22, R-31, R-32, R-33, R-34, R-35, R-36, R-42, R-51, R-52, R-53, R-56, R-63, NFR-10 | S-09, S-10, S-13 (recovery), S-14, S-04 (data) | 2 Aug 2027 – 17 Sep 2027 |
| **M6 Channel record** | R2 features | Approve Gate E, record a manual upload honestly with verification, propose corrections, enter manual metrics, track the 4/4/2/2 slate with variety flags, see the validation dashboard | R-39, R-40, R-41, R-46, R-47, R-48, R-49, R-58, R-60, R-72, NFR-18 | S-12, S-16, S-11 (disclosure) | 20 Sep 2027 – 15 Oct 2027 |
| **M7 Hardening** | Go-live (G5) | Run the product for the public slate: NFRs verified, restore rehearsed, alerts and kill switches drilled, runbook ready | NFR-01, NFR-02, NFR-04, NFR-06, NFR-08, NFR-13, NFR-14, NFR-15 | — (accessibility pass on all) | 18 Oct 2027 – 5 Nov 2027 |
| R2 validation slate | **R2 gate** | Publish the twelve originals (4/4/2/2) through the product with review, effort, cost, rights and publication records | KPI-01–KPI-06, KPI-14 evidence | — | 8 weeks after go-live, to about 31 Dec 2027 |

"Accepted here" lists the requirements whose last spec lands in that milestone; the full map is [below](#requirements-to-milestones). Gate E parts of R-40, R-41 and R-46 land in M6; their Gate A–D parts are accepted for R1 at M5. NFRs are built from M0 and verified in M7.

### M0 Foundation

**Slice.** The walking skeleton (PROCESS.md Milestones): repo, Makefile and Compose stack, CI with security scans, contracts 1.0.0 generated from Pydantic, database with migrations and RLS, the replacement object store, Keycloak sign-in and the app shell, telemetry, the outbox and DBOS workflows, the AG-UI project stream, the agent runtime with a fake model and tool host, the render service skeleton, and the search API choice. 14 specs, 32 spec-days.

**Your tasks in M0** (about 20 hours, PRD M0 discovery):
- twelve briefs across the four series and the first three topics, one mathematical first (Q-02, OOS-002);
- motion and voice references for brand kit v1 (A-31, OOS-003);
- rights and access preflight: font licences into the ledger, ElevenLabs "improve the models" opt-out on every account before the first real call, the YouTube destination account noted for R2 (OOS-004, Q-08, SECURITY.md);
- the manual effort baseline: time one comparable Short made with your current tools (Q-13, KPI-04);
- add the required checks to the `main` ruleset when SPEC-02 merges.

**Exit, beyond G4.** One trivial request goes frontend → backend → agent → database, traced, deployed to staging by `make deploy`; a fresh clone runs with `make setup` and `make up`; conformance C01–C04 pass. Also: the DBOS spike result is recorded in ADR-003 (or ADR-003 is superseded before M1); the object store is chosen and amended into ADR-015; Q-29 is decided with its ADR; the AG-UI SDKs are pinned.

### M1 Feasibility (R0)

**Slice.** Demonstration functions, the compiler, house style, the six animation families, TTS with measured alignment and captions, per-scene clips with cache and manifest, media QA, and `make r0-sample`. 11 specs, 28 spec-days.

**Exit, beyond G4 (PRD §19.3, R0).** One accurate original visual story (odd squares, 30–45 s) with timed narration and captions; a targeted revision (the PRD §10.3 hold) that rebuilds only what changed; measured cost and render time recorded as the NFR-02 baseline; object continuity checked; each of the six families renders in an original vertical story with correct values (R-19).

**Decision point after M1.** As PRD §22.1–22.2 require: re-estimate from measured M0–M1 velocity, confirm Remotion meets the output standard before the Studio is coupled to it, and re-baseline the M2–M7 dates with you.

### M2 Brief to evidence

**Slice.** Projects and the production state machine, settings, the approvals service, budget reservation, brief with series and preflight, the research agent with its SSRF-guarded fetcher and evals, the evidence API, and the Studio frame (run indicator, gate strip, approval dialog, error panel, spend meter) with S-02, S-03, S-04, S-05 and S-13 (inspect and cancel). 15 specs, 33 spec-days.

**Exit, beyond G4.** Conformance C05–C11 pass (the first milestone with approvals, agent runs and budgets; see the deviation note in TEST_STRATEGY.md); research evals meet their thresholds over N = 10 and the thresholds are calibrated; J1 steps 1–5 pass on staging with real providers.

### M3 Script to preview

**Slice.** Demonstrations API with labels, scripts with hook editing, the script agent, the content policy checklist with Gate B, storyboards with compiler errors and the storyboard agent with Gate C, narration takes and pronunciation, preview and hook-only preview, and S-06, S-07 and S-08. 12 specs, 26 spec-days.

**Exit, beyond G4.** Script and storyboard evals meet their thresholds over N = 10 and are calibrated; J1 steps 6–8 pass on staging for the odd-squares story and one other of the first three topics.

### M4 Master to export

**Slice.** Master render with media QA and the QA states, findings and the rubric, the rights ledger and library, package versions with Gate D blockers and the export bundle, the KPI analytics projection, and S-11 and S-15. 8 specs, 19 spec-days.

**Exit, beyond G4.** J1 runs through the Studio from idea to export bundle (T-86, R1 portion); the bundle is never counted as published (R-46); C14 passes for packages.

### M5 Revision and recovery (R1 gate)

**Slice.** The revision graph and impact, redraft through the agents (Q-34), apply with selective rebuild, compare, retry, resume and takeover, cost and effort with the KPI-04 baseline, data export, archive and delete, retention and daily backups with an off-machine copy, and S-09, S-10, S-13, S-14 and S-04's data section. 9 specs, 22 spec-days.

**Exit, beyond G4 (PRD §19.3, R1).** The P0 production journey works through the UI; no unresolved approval-bypass or access-control defects; recovery and provenance are visible and bounded. **R1 completion evidence:** you make the first three topics (Q-02) end to end in the Studio with no normal-use code edits (R-61 AC3), and calibrate the rubric on them (Q-04). J6 passes on staging (T-87). C09 passes for out-of-scope redrafts.

### M6 Channel record (R2 features)

**Slice.** Gate E and the manual publication record with verification and mismatch flags, corrections and manual metrics, AI-production disclosure, the series slate with variety checks, the validation dashboard, and S-12 and S-16. 7 specs, 13 spec-days.

**Exit, beyond G4.** J1 runs to a publication record and J3 runs on staging (T-86, T-88), using a synthetic upload record; the first real record is the first slate video. KPI-01–KPI-06 and KPI-14 compute on the dashboard from events.

### M7 Hardening

**Slice.** Restore rehearsal, performance baseline and SLO calibration (A-15), security scanning and the isolation suite, the Studio accessibility audit, kill switches with credential revocation and audit export, alert drills and runbook entries, and release conformance (C12, C14, chaos). 7 specs, 12 spec-days.

**Exit (G5 go-live).** NFR-01–NFR-19 verified; runbook rehearsed; alerts fire on synthetic faults; restore within RPO 24 h and RTO one working day (A-16); production environment up with its own credentials; a paid ElevenLabs plan in place and the training opt-out confirmed (ADR-013); the public channel identity decided (Q-01).

### After hardening: the R2 validation slate

Go-live (G5) starts the operate phase (PROCESS.md, Operate and support), with two to four weeks of hypercare inside the slate. You produce and publish the twelve originals, 4 What If, 4 Wait How Does That Work, 2 Solve This, 2 Inside the Machine (KPI-01), through the product. Fixes during the slate go through normal `fix/` PRs and patch releases v1.0.x.

**R2 gate (PRD §19.3).** Twelve reviewed originals across the four series, with actual public records, rights, effort, cost and quality results; effort compared with the M0 manual baseline (KPI-04); production reliability reported against the adopted threshold of 10 of 12 without code-level repair (KPI-02, Q-04); every rubric dimension ≥ 4 with no unresolved material error or rights blocker (KPI-03); moat hypotheses 1–3 checked against their PRD §1.1 proof (Q-32). Content time: the PRD's 60–120 hours.

### Conditional, after the R2 gate

Not specced and not dated. Each starts only on your decision, with its own estimate.

| Work | Trigger | Scope in outline |
|---|---|---|
| AWS Mumbai move | R2 gate signed (Q-21, ADR-011) | Terraform, ECS Fargate, RDS, S3 Object Lock, Secrets Manager, Cognito (ADR-012); real budget limits set from measured per-video cost (Q-05) |
| M8 Connected channel (R3) | You promote R3 (A-18) | R-66–R-71: YouTube connection and Instagram eligibility, private upload, release and reconciliation, scheduling, connected verification; S-17, S-18; QA-07. PRD §22.1 says this suite needs its own estimate |
| M9 Learning loop (R3) | After M8 | R-72–R-77: metric import and dictionary, Opportunity Lab, experiments, diagnostic recommendations; S-19, S-20; KPI-07–KPI-13 |

## Dates, demos and UAT

**Capacity is not fixed** (Q-03), so the windows above are computed, not committed. Q-36 asks for your weekly capacity; A-36 assumes **25 hours a week**, a spec-day of about 5 hours, and a 20% buffer per milestone for review, demos, UAT, holidays and surprises. Start: Monday 23 Nov 2026, after G3 and the M0 spec preparation.

| Milestone | Spec-days (+ owner days) | Weeks at 25 h | Proposed window at 25 h/week (A-36) | Weeks at 40 h | Window at 40 h/week |
|---|---|---|---|---|---|
| M0 | 32 (+4) | 9 | 23 Nov 2026 – 22 Jan 2027 | 6 | 23 Nov 2026 – 1 Jan 2027 |
| M1 | 28 | 7 | 25 Jan 2027 – 12 Mar 2027 | 5 | 4 Jan 2027 – 5 Feb 2027 |
| M2 | 33 | 8 | 15 Mar 2027 – 7 May 2027 | 5 | 8 Feb 2027 – 12 Mar 2027 |
| M3 | 26 | 7 | 10 May 2027 – 25 Jun 2027 | 4 | 15 Mar 2027 – 9 Apr 2027 |
| M4 | 19 | 5 | 28 Jun 2027 – 30 Jul 2027 | 3 | 12 Apr 2027 – 30 Apr 2027 |
| M5 | 22 (+4) | 7 | 2 Aug 2027 – 17 Sep 2027 | 4 | 3 May 2027 – 28 May 2027 |
| M6 | 13 | 4 | 20 Sep 2027 – 15 Oct 2027 | 2 | 31 May 2027 – 11 Jun 2027 |
| M7 | 12 | 3 | 18 Oct 2027 – 5 Nov 2027 | 2 | 14 Jun 2027 – 25 Jun 2027 |

At 25 h/week, go-live is about **5 Nov 2027** and the R2 gate about **31 Dec 2027**; at 40 h/week, about **25 Jun 2027** and **20 Aug 2027**.

**What to agree at G3:** the capacity (Q-36) and the M0 and M1 windows. M2–M7 are indicative until the re-estimate at M1 exit, because PRD §22.2 ties calendar commitments to the measured spike.

**Demos and UAT.** The last two working days of each window: a demo of the slice, then your UAT walkthrough from the milestone's acceptance criteria (T-89, `plans/Mx/uat.md`, drafted in Stage 5). G4 is signed the following working day. A short weekly update is generated from STATUS.md (PROCESS.md, Tracking).

**Estimate against the PRD.** PRD §22.1 allows 228–364 engineering hours plus 60–120 content hours for a "narrow internal release". This plan is **185 spec-days, about 925 engineering hours**, plus about 40 hours of your discovery and UAT time and the PRD's 60–120 content hours: roughly two and a half times the PRD's upper bound. The difference is the baseline agreed in Stages 1–2: sixteen Studio screens with every state, the agent runtime, AG-UI stream and conformance suite (ADR-020, ADR-021), revision redraft through agents (Q-34), approval policy versions (Q-35), local staging and production environments (ADR-022) and the full test levels. Treat it as ±30% until M1 is measured.

**If the calendar is too long**, the levers in order of effect are: more weekly capacity; fewer R1 extras (compare as a text diff only, a read-only S-14, a basic S-15: about 4 spec-days); and nothing else of size, because the remaining specs carry Must requirements. The PRD §22.1 smaller January launch stays off the table (Q-03).

## Requirements to milestones

Every Must R-xx and every NFR-xx is in a milestone (checked by script). "Starts" is the first milestone with a spec for it; "Accepted at" is where its last spec lands. Should requirements R-66–R-77 are R3 except the manual part of R-72 (KPI-06) and the manual states of R-48.

| Requirement | Priority | Specs | Starts | Accepted at |
|---|---|---|---|---|
| R-01 | Must | SPEC-04, SPEC-06, SPEC-07, SPEC-26, SPEC-36 | M0 | M2 |
| R-02 | Must | SPEC-18, SPEC-27, SPEC-37, SPEC-55, SPEC-59 | M1 | M4 |
| R-03 | Must | SPEC-21, SPEC-27, SPEC-37, SPEC-48, SPEC-49 | M1 | M3 |
| R-04 | Must | SPEC-27, SPEC-37, SPEC-56, SPEC-58 | M2 | M4 |
| R-05 | Must | SPEC-06, SPEC-07, SPEC-28, SPEC-35 | M0 | M2 |
| R-06 | Must | SPEC-30, SPEC-38 | M2 | M2 |
| R-07 | Must | SPEC-16, SPEC-30, SPEC-38, SPEC-46, SPEC-51 | M1 | M3 |
| R-08 | Must | SPEC-14, SPEC-31, SPEC-32, SPEC-33, SPEC-39 | M0 | M2 |
| R-09 | Must | SPEC-31, SPEC-39, SPEC-44, SPEC-56 | M2 | M4 |
| R-10 | Must | SPEC-31, SPEC-39 | M2 | M2 |
| R-11 | Must | SPEC-15, SPEC-41, SPEC-45 | M1 | M3 |
| R-12 | Must | SPEC-15, SPEC-17, SPEC-41, SPEC-45 | M1 | M3 |
| R-13 | Must | SPEC-41, SPEC-44, SPEC-45 | M3 | M3 |
| R-14 | Must | SPEC-42, SPEC-43, SPEC-45 | M3 | M3 |
| R-15 | Must | SPEC-42, SPEC-45, SPEC-50, SPEC-52 | M3 | M3 |
| R-16 | Must | SPEC-25, SPEC-46, SPEC-47, SPEC-51 | M1 | M3 |
| R-17 | Must | SPEC-42, SPEC-45 | M3 | M3 |
| R-18 | Must | SPEC-03, SPEC-16, SPEC-46, SPEC-47, SPEC-51 | M0 | M3 |
| R-19 | Must | SPEC-19, SPEC-20, SPEC-52 | M1 | M3 |
| R-20 | Must | SPEC-17, SPEC-19, SPEC-20, SPEC-51 | M1 | M3 |
| R-21 | Must | SPEC-16, SPEC-22, SPEC-51 | M1 | M3 |
| R-22 | Must | SPEC-17, SPEC-20, SPEC-46, SPEC-51, SPEC-61 | M1 | M5 |
| R-23 | Must | SPEC-17, SPEC-18, SPEC-52 | M1 | M3 |
| R-24 | Could | — | — | Not planned |
| R-25 | Must | SPEC-21, SPEC-48, SPEC-49 | M1 | M3 |
| R-26 | Must | SPEC-22, SPEC-48, SPEC-49 | M1 | M3 |
| R-27 | Must | SPEC-17, SPEC-22, SPEC-24, SPEC-52 | M1 | M3 |
| R-28 | Must | SPEC-50, SPEC-52 | M3 | M3 |
| R-29 | Must | SPEC-12, SPEC-23, SPEC-24, SPEC-53, SPEC-57 | M0 | M4 |
| R-30 | Must | SPEC-05, SPEC-23, SPEC-53, SPEC-57 | M0 | M4 |
| R-31 | Must | SPEC-25, SPEC-61, SPEC-62, SPEC-64 | M1 | M5 |
| R-32 | Must | SPEC-23, SPEC-25, SPEC-61, SPEC-63, SPEC-64 | M1 | M5 |
| R-33 | Must | SPEC-63, SPEC-65 | M5 | M5 |
| R-34 | Must | SPEC-27, SPEC-29, SPEC-35, SPEC-37, SPEC-67 | M2 | M5 |
| R-35 | Must | SPEC-21, SPEC-25, SPEC-29, SPEC-67 | M1 | M5 |
| R-36 | Must | SPEC-25, SPEC-60, SPEC-67 | M1 | M5 |
| R-37 | Must | SPEC-54, SPEC-56, SPEC-57 | M4 | M4 |
| R-38 | Must | SPEC-54, SPEC-57 | M4 | M4 |
| R-39 | Must | SPEC-74, SPEC-75 | M6 | M6 |
| R-40 | Must | SPEC-28, SPEC-35, SPEC-38, SPEC-45, SPEC-51, SPEC-58, SPEC-70 | M2 | M6 |
| R-41 | Must | SPEC-28, SPEC-35, SPEC-70 | M2 | M6 |
| R-42 | Must | SPEC-28, SPEC-42, SPEC-61, SPEC-63, SPEC-64 | M2 | M5 |
| R-43 | Must | SPEC-28 | M2 | M2 |
| R-44 | Must | SPEC-26, SPEC-35, SPEC-36, SPEC-53 | M2 | M4 |
| R-45 | Must | SPEC-56, SPEC-58 | M4 | M4 |
| R-46 | Must | SPEC-56, SPEC-58, SPEC-70, SPEC-72 | M4 | M6 |
| R-47 | Must | SPEC-70, SPEC-72 | M6 | M6 |
| R-48 | Must | SPEC-70, SPEC-72 | M6 | M6 |
| R-49 | Must | SPEC-71, SPEC-72 | M6 | M6 |
| R-50 | Must | SPEC-09, SPEC-10, SPEC-34, SPEC-40 | M0 | M2 |
| R-51 | Must | SPEC-09, SPEC-66 | M0 | M5 |
| R-52 | Must | SPEC-40, SPEC-66 | M2 | M5 |
| R-53 | Must | SPEC-34, SPEC-40, SPEC-66 | M2 | M5 |
| R-54 | Must | SPEC-53, SPEC-56, SPEC-58 | M4 | M4 |
| R-55 | Must | SPEC-18, SPEC-48, SPEC-55, SPEC-58, SPEC-59 | M1 | M4 |
| R-56 | Must | SPEC-68 | M5 | M5 |
| R-57 | Must | SPEC-30, SPEC-38, SPEC-43 | M2 | M3 |
| R-58 | Must | SPEC-74, SPEC-75, SPEC-76 | M6 | M6 |
| R-59 | Must | SPEC-44, SPEC-45, SPEC-56 | M3 | M4 |
| R-60 | Must | SPEC-73 | M6 | M6 |
| R-61 | Must | SPEC-07, SPEC-10, SPEC-34, SPEC-35 | M0 | M2 |
| R-62 | Must | SPEC-55, SPEC-59 | M4 | M4 |
| R-63 | Must | SPEC-11, SPEC-33, SPEC-40, SPEC-43, SPEC-47, SPEC-62 | M0 | M5 |
| R-64 | Could | — | — | Not planned |
| R-65 | Could | — | — | Not planned |
| R-66 | Should | — | — | R3, conditional (A-18) |
| R-67 | Should | — | — | R3, conditional (A-18) |
| R-68 | Should | — | — | R3, conditional (A-18) |
| R-69 | Should | — | — | R3, conditional (A-18) |
| R-70 | Should | — | — | R3, conditional (A-18) |
| R-71 | Should | — | — | R3, conditional (A-18) |
| R-72 | Should | SPEC-71, SPEC-72 | M6 | M6 |
| R-73 | Should | — | — | R3, conditional (A-18) |
| R-74 | Should | — | — | R3, conditional (A-18) |
| R-75 | Should | — | — | R3, conditional (A-18) |
| R-76 | Should | — | — | R3, conditional (A-18) |
| R-77 | Should | — | — | R3, conditional (A-18) |
| R-78 | Won't | — | — | Out of scope |
| R-79 | Won't | — | — | Out of scope |
| R-80 | Won't | — | — | Out of scope |
| R-81 | Won't | — | — | Out of scope |
| R-82 | Won't | — | — | Out of scope |
| NFR-01 | Must | SPEC-09, SPEC-83 | M0 | M7 |
| NFR-02 | Must | SPEC-25, SPEC-78 | M1 | M7 |
| NFR-03 | Must | SPEC-23 | M1 | M1 |
| NFR-04 | Must | SPEC-04, SPEC-05, SPEC-06, SPEC-10, SPEC-26, SPEC-79 | M0 | M7 |
| NFR-05 | Must | SPEC-02, SPEC-11, SPEC-16, SPEC-32, SPEC-33 | M0 | M2 |
| NFR-06 | Must | SPEC-02, SPEC-08, SPEC-79, SPEC-81 | M0 | M7 |
| NFR-07 | Must | SPEC-29 | M2 | M2 |
| NFR-08 | Must | SPEC-18, SPEC-24, SPEC-80 | M1 | M7 |
| NFR-09 | Must | SPEC-08, SPEC-13 | M0 | M0 |
| NFR-10 | Must | SPEC-68, SPEC-69 | M5 | M5 |
| NFR-11 | Must | SPEC-03, SPEC-11, SPEC-14, SPEC-21 | M0 | M1 |
| NFR-12 | Must | SPEC-12, SPEC-16 | M0 | M1 |
| NFR-13 | Must | SPEC-01, SPEC-02, SPEC-04, SPEC-13, SPEC-83 | M0 | M7 |
| NFR-14 | Must | SPEC-69, SPEC-77 | M5 | M7 |
| NFR-15 | Must | SPEC-08, SPEC-81, SPEC-82 | M0 | M7 |
| NFR-16 | Must | SPEC-16 | M1 | M1 |
| NFR-17 | Must | SPEC-33, SPEC-43, SPEC-47 | M2 | M3 |
| NFR-18 | Must | SPEC-02, SPEC-70, SPEC-72 | M0 | M6 |
| NFR-19 | Must | SPEC-03 | M0 | M0 |

## RAID

### Risks

| Risk | Likelihood | Impact | Response | Watch |
|---|---|---|---|---|
| Effort is about 2.5× the PRD allowance, so the calendar runs long | High | High | Re-estimate at M1 exit; agree capacity (Q-36); levers above | Velocity per milestone in retros |
| DBOS fails the kill-and-resume spike (ADR-003) | Low | High | SPEC-09 runs it first; if it fails, supersede ADR-003 before M1 depends on it | SPEC-09 result |
| Remotion cannot meet the output standard or render time (NFR-02, ADR-002) | Medium | High | Measured in M1; renderer confirmed before the Studio couples to it (PRD §22.2) | T-52 baseline |
| Animation, typography and audio polish take longer than sized (PRD §22.1) | High | Medium | M1 is media-only so it shows early; families are small and reviewed | M1 velocity |
| Agent output below the eval thresholds | Medium | Medium | Iterate prompts inside the spec; manual takeover remains (R-51); simplify the task | T-60 baselines at M2, M3 |
| AG-UI SDK changes before 1.0 | Medium | Low | Pinned; upgrades are their own spec (ADR-020) | Renovate PRs |
| Your machine is the only host | Medium | High | Daily backups with an off-machine copy from M5 (SPEC-69); data before then is synthetic; branches pushed daily | `oos.backup.age_seconds` |
| One person reviews every PR and signs every gate | High | Medium | WIP limit of two, Claude review first, small specs | PR age |
| Free credits run out during development or evals (Q-05 parked) | Medium | Medium | Fakes by default; weekly live evals at N = 3; spend recorded; limits set before the AWS move | Cost dashboard |
| GitHub Actions minutes allowance exceeded | Medium | Low | Path filters, caches, nightly skips when `main` is unchanged; renders off PRs | Minutes at each retro |
| Cursor drifts from conventions | Medium | Medium | Rules fixed in the same PR; Claude review against CLAUDE.md | Repeated review comments |
| Contract churn breaks parallel work | Medium | Medium | Contracts first, in their own PR, with a version bump (contracts.mdc) | Contract PRs per milestone |
| Incorrect facts or visuals (PRD §25) | Medium | High | Claim review, verified demonstrations, "needs specialist" blocks (A-04) | KPI-03 findings |
| Generic or repeated output across the slate (PRD §25) | Medium | Medium | Variety check before Gate D (R-39), rubric | S-16 flags |
| Provider terms, prices or the Remotion licence change | Low | Medium | Adapters (ADR-009); terms re-checked at first real call and on change | SECURITY.md provider table |
| Three Compose stacks exhaust one machine | Medium | Low | Staging runs only during release-candidate checks; production from G5 | Host memory |

### Assumptions

| Assumption | Source | If wrong |
|---|---|---|
| 25 hours a week, 5 hours per spec-day, 20% buffer | A-36 (Q-36 open) | Dates move proportionally |
| One implementer (you) with Cursor; Claude reviews; you approve | Project instructions, A-23 | Tracks allow more in parallel |
| Development runs on free provider credits; costs recorded | Q-05 | Eval cadence drops; limits set earlier |
| The `main` ruleset is enforced (GitHub Pro or Team) with enough Actions minutes | PROCESS.md CI/CD practices | Required checks become advisory; fewer nightly runs |
| The first three topics fit the six initial families | Q-02, R-19 | A new family is an R-24 (Could) estimate |
| R1 and R2 run locally; staging and production are local Compose projects | ADR-011, ADR-022 | AWS move earlier, with its own estimate |
| Eval rate thresholds are provisional until calibrated at M2 and M3 | TEST_STRATEGY.md | Thresholds change through that table |

### Issues

| Issue | Status | Action |
|---|---|---|
| G2 sign-off is not recorded in STATUS.md (all checks pass; screens approved 14 Nov) | Open | You record the G2 signature |
| Q-36 weekly capacity | Open | You answer at G3 |
| Q-29 search API | Open | Decided in SPEC-14 (M0) |
| Q-05 budget limits | Parked | Set before the AWS move |
| Contracts are 0.4.0 drafts | Expected | Regenerated as 1.0.0 by SPEC-03 |

### Dependencies

| Dependency | Needed by | Owner |
|---|---|---|
| OpenAI and ElevenLabs keys for development, ElevenLabs training opt-out | SPEC-11, SPEC-21 (M0–M1) | You |
| Search API account | SPEC-14 (M0) | You, after the choice |
| Twelve briefs, first three topics, motion and voice references, manual baseline | M0 | You |
| UAT sessions at each milestone; the first three videos for the R1 gate | M1–M7 | You |
| Paid ElevenLabs plan; public channel identity (Q-01); YouTube destination account (Q-08) | Go-live, before the first public upload | You |
| Pinned versions: DBOS, Remotion 4.0.x, AG-UI SDKs, Keycloak | M0 | Tech lead |
| Open-licence fonts in the rights ledger | SPEC-18 (M1) | You |
