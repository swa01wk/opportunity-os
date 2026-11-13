# Requirements

Baseline derived from [PRD v2.0](../sources/PRD-v2.0.md) (revised in discovery on 13 Nov 2026: §1.1 added). Revised in discovery on 14 Nov 2026 by product-owner decisions Q-34 (R-31 AC3) and Q-35 (R-41 AC3). Status: **Draft for G1**. Baselined at G1; after that it changes only through change control ([PROCESS.md](../PROCESS.md#tracking-and-change-control)). Open gaps and the assumptions we build on live in [QUESTIONS.md](QUESTIONS.md).

## Summary

OpportunityOS is an internal studio that turns a viewer question into an original, narrated 9:16 animated explainer with claim evidence, human review gates, version-bound approval and verified publication records, then learns from channel data. This baseline targets R0 → R1 → R2 (PRD §4). R3 is planned as Should and is conditional on the R2 gate. R4/R5 are recorded as Won't.

Counts: 82 functional requirements (R-01–R-82), 19 non-functional (NFR-01–NFR-19), 14 KPIs (KPI-01–KPI-14), 21 features (F-01–F-21).

## Conventions

- **IDs.** PRD IDs are kept as references and never renumbered: FR-01–30, CR-01–10, US-01–26, J1–J8, P01–P06, QA-01–12, DEC-01–12, OOS-001–027. PRD milestones are written "PRD M0–M6"; PRD platform references are "ref S1–S14"; PRD gates A–E are in-app review gates, not delivery gates G1–G5.
- **Priority (MoSCoW).** PRD P0 = **Must**. PRD P1 (R3) = **Should**, planned as a later milestone. PRD P2/P3 (R4/R5) = **Won't** for this baseline. **Could** marks behaviour the PRD calls optional.
- **Release.** The earliest PRD release (§4) at which the requirement is accepted. "R0 sample" means R0 demonstrates a subset, normally through a command-line pipeline with technical help (PRD §4, §14.2).
- **Trace line.** Each requirement lists its PRD sections, the FR/CR it comes from, the user stories it serves and the PRD QA checks that verify it. QA-xx become T-xx in `TEST_STRATEGY.md` (Stage 3).
- **Roles, not personas.** Actions are authorised by responsibility (owner, editor, reviewer, publisher, analyst; PRD §2.3). In R1 one authenticated owner holds all of them. Agents never approve anything.
- **Acceptance criteria** use Given / When / Then. Every Must has at least one; Won't items record the PRD's acceptance evidence for later.

## Product framing

The PRD owns these; this baseline traces to them (PROCESS.md, Stage 1 product framing).

- **Personas:** P01–P06 ([PRD §2.1](../sources/PRD-v2.0.md#21-persona-definitions)). R1–R2 build for P01 and P02 only.
- **User journeys:** J1–J8 ([PRD §6.2–6.10](../sources/PRD-v2.0.md#62-journey-map)). In scope: J1, J6 and J3; J2 and J4 are R3 (Should); J5, J7 and J8 are Won't.
- **User stories:** US-01–US-26 ([PRD §6.1](../sources/PRD-v2.0.md#61-user-story-catalogue)). Each R-xx lists the stories it serves.
- **Agent steps:** which journey steps an agent performs, what it prepares, who decides, and each workflow's maturity level (Q-33): [AGENT_ARCHITECTURE.md](../architecture/AGENT_ARCHITECTURE.md#maturity-per-workflow).
- **Value and defensibility:** problems solved and moat hypotheses 1–4 ([PRD §1.1](../sources/PRD-v2.0.md#11-what-the-product-solves-and-defensibility)). The KPIs that test each hypothesis are in [KPIs and the moat hypotheses](#kpis-and-the-moat-hypotheses).

## Features (F-xx)

| Feature | Name | Requirements | Main PRD sections | Journeys | Priority |
|---|---|---|---|---|---|
| F-01 | Workspace, brand and project setup | R-01–R-05 | §2.3, §4, §7.1 | J1, J3 | Must |
| F-02 | Idea intake and brief | R-06–R-07 | §7.2, §9.1 | J1 | Must |
| F-03 | Research, claims and evidence | R-08–R-10 | §14.1, §15 | J1, J6 | Must |
| F-04 | Verified demonstrations | R-11–R-13 | §9.2, §19.1 | J1 | Must |
| F-05 | Script and storyboard | R-14–R-17 | §7.2, §14.1 | J1 | Must |
| F-06 | Signal Motion Engine | R-18–R-24 | §5.2, §9.1–9.2 | J1 | Must (R-24 Could) |
| F-07 | Narration, timing and captions | R-25–R-27 | §9.2, §10.2 | J1 | Must |
| F-08 | Preview and master render | R-28–R-30 | §7.2, §9.3 | J1 | Must |
| F-09 | Targeted revision | R-31–R-33 | §9.3, §10.3 | J6 | Must |
| F-10 | Cost and effort control | R-34–R-36 | §21.1 | J1, J6 | Must |
| F-11 | Quality review | R-37–R-39 | §19.1 | J1, J3 | Must |
| F-12 | Approval governance | R-40–R-44 | §8.1–8.2 | J1, J6 | Must |
| F-13 | Package, export and manual publication | R-45–R-49 | §8.2, §16 | J1 | Must |
| F-14 | Runs, recovery and cancellation | R-50–R-53 | §13, §20 | J6 | Must |
| F-15 | Provenance, rights and data control | R-54–R-56 | §5.2, §15 | J1, J6 | Must |
| F-16 | Editorial series and content policy | R-57–R-60 | §5.1–5.2 | J3 | Must |
| F-17 | Studio and agent tasks | R-61–R-65 | §13, §14.1 | J1 | Must (R-64, R-65 Could) |
| F-18 | Channel connection | R-66–R-67 | §7.1, §16 | J1, J2 | Should (R3) |
| F-19 | Connected publishing | R-68–R-71 | §8.2, §16 | J1 | Should (R3) |
| F-20 | Audience learning and experiments | R-72–R-77 | §17–18 | J2, J4 | Should (R3) |
| F-21 | Customer and business expansion | R-78–R-82 | §2.1, §6, §11 | J5, J7, J8 | Won't |

## Functional requirements (R-xx)

### F-01 Workspace, brand and project setup

#### R-01 Workspace, owner and projects
Must · R1 · PRD §2.3, §4, §11 · FR-01, FR-29 · US-01 · QA-10

- AC1: Given an unauthenticated request, when it targets any Studio page or API, then it is refused and no workspace data is returned.
- AC2: Given the authenticated owner, when they create a project, then the project, its settings and every record, artifact, job and export created under it are scoped to the one workspace.

#### R-02 Versioned brand kit
Must · R1 (R0 sample: one theme) · PRD §5.2, §9.3, §11 · FR-01 · US-01 · QA-04

- AC1: Given a project, when a render is produced, then the exact brand-kit version is pinned in its manifest.
- AC2: Given approved or published renders, when the brand default changes, then those renders are not mutated and the change shows which draft scenes it would invalidate.

#### R-03 Narrator settings
Must · R1 · PRD §4, §7.1 · FR-06 · US-01, US-07

- AC1: Given the workspace's one licensed English narrator, when a project is created, then its voice settings are stored and pinned per narration take.

#### R-04 Destination channel profile
Must · R1 · PRD §7.1 · FR-02 · US-01

- AC1: Given a project, when the destination is set, then platform, account label, timezone, export profile and disclosure settings are stored; times display in the selected timezone (initially Asia/Kolkata) and are stored as absolute timestamps.
- AC2: Given a package, when the audience / made-for-kids setting is empty, then package approval is blocked until the operator sets it explicitly; the system never defaults it from "educational".
- AC3: Given a configured reference or example channel, when choosing a destination, then it cannot be selected as the destination.

#### R-05 Responsibilities and authority
Must · R1 · PRD §2.3, §3, §8.1 · FR-09 · US-12 · QA-05

- AC1: Given an action (draft, review, approve package, release, analyse), when it is attempted, then it is checked against the actor's responsibility and scope; administration, reviewer sign-off and analytics access never imply publishing or budget authority.
- AC2: Given R1, when one owner holds every responsibility, then each approval still records which responsibility it was given under.

### F-02 Idea intake and brief

#### R-06 Content Opportunity Contract
Must · R1 · PRD §1, §7.2 stages 1–2, §15 · FR-02 · US-02 · QA-09

- AC1: Given an idea or proposal, when the operator captures it, then an editable contract persists audience, viewer question, promise/payoff, series and format, evidence plan, proposed animation family, budget allowance, destination, hypothesis and measurement plan.
- AC2: Given an accepted contract, when downstream artifacts are created, then each links back to it, so the final publication and outcomes trace to the original need.

#### R-07 Capability, rights and budget preflight
Must · R1 (R0 sample: capability check) · PRD §7.2 stage 6, §9.1, §11 · FR-22 · US-02 · QA-01

- AC1: Given a brief or storyboard, when it needs a visual operation no supported component provides, then the gap is shown before any paid task is dispatched.
- AC2: Given missing asset rights or a budget allowance below the estimate, when production is requested, then dispatch is blocked with the specific gap listed.

### F-03 Research, claims and evidence

#### R-08 Research task and claim ledger
Must · R1 · PRD §14.1, §15 · FR-03 · US-03 · QA-08

- AC1: Given an accepted brief, when research runs, then each material claim is recorded with type, source metadata, URL, retrieval time, supporting location or permitted excerpt, contradictions and reviewer status.
- AC2: Given a cited source, when it is stored, then the citation is validated (reachable, locates the supporting text), not just checked for URL existence.

#### R-09 Unsupported claims block approval
Must · R1 · PRD §8.1 gate B, §19.1 · FR-03, CR-03 · US-03, US-11 · QA-08

- AC1: Given an unsupported or contradicted claim, when Gate B or D approval is requested, then approval is blocked until the claim is resolved, removed or accurately qualified.
- AC2: Given a claim the operator cannot credibly verify, when it is marked "needs specialist", then only a reviewer with that assigned scope can clear it.

#### R-10 Claim traceability
Must · R1 · PRD §15 · FR-03, FR-04, FR-10 · US-03

- AC1: Given a script beat or scene, when the reviewer selects a claim, then its sources, location, review state and every beat and scene that use it are shown.

### F-04 Verified demonstrations

#### R-11 Demonstration model
Must · R0 · PRD §9.2, §10.1, §15 · FR-20 · US-04 · QA-02

- AC1: Given reviewed parameters, when the demonstration is computed, then counts, units, coordinates and relationships come only from reviewed allowlisted functions, using exact arithmetic or a documented tolerance and rounding.
- AC2: Given the odd-numbers storyboard (PRD §10), when layer k is added, then it contains exactly 2k − 1 cells and cumulative totals are 1, 4, 9, 16, 25.

#### R-12 Mismatch blocks progression
Must · R0 · PRD §9.2 · FR-20, CR-03 · US-04 · QA-02

- AC1: Given a displayed value, equation term or geometry that differs from the computed model, or an input outside its domain, when the scene is validated, then progression stops and the error names the scene, object and expected value.

#### R-13 Approximations and illustrations labelled
Must · R1 · PRD §5.1, §9.2, §19.1 · CR-03 · US-04

- AC1: Given a demonstration, when it is an example, approximation or illustrative model rather than a general proof or measurement, then it is labelled as such in the storyboard and reviewed at Gate B.
- AC2: Given illustrative animation, when it depicts a real-world event, then it is never presented as a measured simulation or footage.

### F-05 Script and storyboard

#### R-14 Script with claim references
Must · R1 · PRD §5.2, §7.2 stage 4, §14.1 · FR-04 · US-05

- AC1: Given an approved explanation, when the script task runs, then it returns structured beats (hook, setup, demonstration, explanation, payoff, closure as applicable) with narration and claim IDs.
- AC2: Given an approved script, when narration or a claim reference changes materially, then a new script version is created and the dependent reviews reopen (R-42).

#### R-15 Editable opening and hook
Must · R1 · PRD §5.2, §12 · CR-02 · US-05

- AC1: Given a project, when the operator edits the hook, then it can be previewed on its own and compatible unrelated scenes are reused.

#### R-16 Storyboard task
Must · R1 (R0 sample) · PRD §7.2 stage 5, §14.1 · FR-04, FR-05 · US-06

- AC1: Given an approved script, when the storyboard task runs, then each scene card lists objects, supported actions, timing and the narration it serves, validated by the compiler (R-18).
- AC2: Given an invalid action, when the storyboard is validated, then the affected scene and object are identified.

#### R-17 Layers reviewed independently
Must · R1 · PRD §7.2 · FR-04 · US-05, US-06

- AC1: Given a project, when the operator opens script, storyboard, render or package, then each can be inspected, revised and approved without reopening the others unless a dependency changed.

### F-06 Signal Motion Engine

#### R-18 Typed scene specification
Must · R0 · PRD §9.1, §9.2, §15 · FR-05 · US-06 · QA-01

- AC1: Given a scene spec, when it is compiled, then it is validated against a versioned schema and maps only to reviewed components (see NFR-05).
- AC2: Given an unknown action, missing object, claim or asset reference, out-of-bounds timing or too many objects, when compiled, then it fails with an actionable error naming the scene and field.

#### R-19 Six initial animation families
Must · R0 · PRD §9.1 · FR-05, FR-19

- AC1: Given the scene library, when R0 is assessed, then MathExpression, NumberSequence, GeometricArrangement, ObjectTransform, FocusHighlight and CaptionAndTakeaway each render in an original vertical story with correct values.

#### R-20 Persistent visual objects
Must · R0 · PRD §9.2 · FR-19 · US-06 · QA-04

- AC1: Given an object with a stable ID, when it moves, regroups or transforms, then its identity, colour and meaning persist, and value transformations explicitly map old terms to new.
- AC2: Given colour-coded meaning, when it is shown, then it is also carried by position, label or highlight.

#### R-21 Action timeline
Must · R0 · PRD §9.2 · FR-05, FR-21

- AC1: Given a timeline, when validated, then every action has a supported operation, target IDs, a frame interval at the pinned frame rate, bounded parameters, an easing token and an optional event or phrase anchor.

#### R-22 Scene state and continuity
Must · R1 · PRD §9.2 · FR-07, FR-19 · QA-04

- AC1: Given consecutive scenes, when rendered, then each scene's entry and exit state is persisted and continuity at the cut is checked.
- AC2: Given a change to a scene's exit state, when saved, then the following scenes that inherit it are marked invalid.

#### R-23 Original house style
Must · R0 (first theme) · PRD §5.2, §10.1 · FR-01

- AC1: Given the house style, when defined, then it specifies palette, type scale, equation typography, caption placement, safe zones, transitions, narration voice, pacing and a discreet brand cue, derived only from PRD §5.2 and §10.
- AC2: Given a frame, when reviewed, then the brand cue and decoration do not obstruct the opening or the explanation.

#### R-24 Further semantic families when justified
Could · R2+ · PRD §9.1

- AC1: Given a selected brief that needs a family from the PRD §9.1 expansion list, when it is added, then it has a reviewed component, fixtures and an explicit estimate.

### F-07 Narration, timing and captions

#### R-25 Narration and pronunciation
Must · R0 · PRD §7.2 stage 7 · FR-06 · US-07

- AC1: Given an approved script, when narration is generated, then the operator can audition per scene and adjust pronunciation (including notation) before the master.

#### R-26 Measured timing and alignment
Must · R0 · PRD §9.2 · FR-21 · US-07 · QA-03

- AC1: Given generated audio, when timing is compiled, then measured duration and phrase timestamps, not model estimates, set scene and action timing.
- AC2: Given a new take that no longer fits, when timing is recompiled, then affected alignment updates and the operator is shown the pacing change instead of a silent speed-up.

#### R-27 Readable captions
Must · R0 · PRD §5.2, §10.2 · FR-06 · QA-03

- AC1: Given narration, when captions are built, then they are phrase-segmented, readable at phone size, inside safe zones and never cover active objects, labels or equations.

### F-08 Preview and master render

#### R-28 Draft preview
Must · R1 · PRD §7.2 stage 8 · FR-06 · US-08

- AC1: Given validated inputs, when a preview is rendered, then it is cheaper than the master, records its exact inputs and spend, and shows any generation or layout failure.

#### R-29 Master render and media checks
Must · R0 · PRD §4, §7.2 stage 10 · FR-06 · US-08 · QA-03

- AC1: Given an approved storyboard, when the master renders, then it is 1080×1920 at 30 fps and passes independent checks for dimensions, duration, audio, caption bounds, label overflow and safe zones.

#### R-30 Immutable master and manifest
Must · R1 · PRD §7.2 stage 10, §9.3, §15 · FR-10

- AC1: Given a master, when it is stored, then it is immutable and has a manifest with input hashes, fonts, renderer, codec and component versions, seeds and timing.
- AC2: Given the same pinned inputs, when re-rendered, then the output matches within the documented encoding tolerance (NFR-03).

### F-09 Targeted revision

#### R-31 Revision request and impact review
Must · R1 (R0 sample) · PRD §9.3, §10.3, §13 · FR-07 · US-09

- AC1: Given a requested change on a claim, scene or object, when the operator asks for it, then before regeneration they see the artifacts to rebuild and reuse, estimated cost, timing shifts and approvals that will reopen.
- AC2: Given the PRD §10.3 example ("hold two seconds longer"), when previewed, then later offsets are shown as shifting, with the option to shorten another beat.
- AC3 (Q-34): Given a revision request on a claim, beat, scene or object, when the operator submits it, then the script or storyboard agent redrafts only the targeted beats or scenes as a new draft version; changes outside the target are rejected; the operator sees the redraft and its impact (AC1) before anything is rendered, and can still edit the draft by hand.

#### R-32 Dependency-aware reuse
Must · R0 · PRD §9.3 · FR-07 · US-09 · QA-04

- AC1: Given a change, when regeneration runs, then only artifacts whose effective input hash changed are rebuilt; text changes propagate to TTS, alignment, captions, clip, transitions and mix; duration changes shift assembly and caption offsets; brand or narrator changes invalidate every affected scene.
- AC2: Given any changed effective input, when regeneration completes, then a new master is reassembled even if most clips were reused.

#### R-33 Version history and comparison
Must · R1 · PRD §8.1 · FR-07 · US-09, US-11

- AC1: Given a revised version, when the reviewer opens it, then they can compare it with the previously reviewed version, and earlier approved or published masters remain in history.

### F-10 Cost and effort control

#### R-34 Budget reservation
Must · R1 · PRD §20, §21.1 · FR-08, FR-22 · US-10

- AC1: Given a per-video allowance, when tasks are dispatched (including in parallel), then their estimated cost is reserved first and dispatch pauses when the remaining allowance is insufficient.
- AC2: Given an approved budget, when work later needs new spend outside it, then new authority is required.

#### R-35 Cost records
Must · R0 · PRD §21.1 · FR-08 · US-10

- AC1: Given any task attempt, when it ends, then estimated and actual cost are recorded, including failed and revised attempts, with currency and rate where converted.
- AC2: Given an approved video, when cost is reported, then the denominator is approved outputs, with fixed infrastructure and licensing reported separately.

#### R-36 Effort, quality and revision measurement
Must · R1 (R0: cost and render time) · PRD §19.3, §21.1 · FR-30

- AC1: Given an approved video, when it is closed, then active human minutes, rubric scores, revision count and total cost are recorded against it.

### F-11 Quality review

#### R-37 Findings and disposition
Must · R1 · PRD §19.1 · CR-03 · US-11 · QA-08

- AC1: Given a review, when an issue is raised, then it links to a claim, scene, object or asset and has a disposition.
- AC2: Given an open material factual error or rights blocker, when package approval is requested, then it is refused.

#### R-38 Editorial rubric on the final master
Must · R1 · PRD §19.1 · CR-03 · US-11

- AC1: Given a final-quality master (not only the draft), when it is reviewed, then correctness, clarity, original value, readability (including muted with captions) and promise/payoff are each scored, and the adopted threshold (see Q-04) is enforced.

#### R-39 Slate variety check
Must · R2 · PRD §5.1 · CR-04 · US-21

- AC1: Given the slate, when reviewed, then near-identical stories, wording and scene patterns across episodes are flagged before package approval.

### F-12 Approval governance

#### R-40 In-app review gates A–E
Must · R1 · PRD §8.1 · FR-09 · US-12

- AC1: Given gates A (brief), B (explanation and script), C (storyboard), D (final package) and E (public release), when each is approved, then the evidence the PRD lists for it is shown and recorded; related reviews may share a screen but keep separate scope.

#### R-41 Version-bound approval
Must · R1 · PRD §8.1 · FR-09 · US-12 · QA-05

- AC1: Given an approval, when recorded, then it binds actor, responsibility, immutable target version or hash, action scope, destination account where relevant and timestamp.
- AC2: Given a target that has changed since approval, when an action relies on it, then the stale approval is rejected.
- AC3 (Q-35): Given an approval, when recorded, then it also stores the brand-kit, rubric and content-policy versions in force; when the rubric or content policy changes, Gate D reopens for packages not yet published; a Gate E approval for a scheduled release lapses if its approved time passes with no recorded publication. Approvals have no other time expiry.

#### R-42 Changes reopen approvals
Must · R1 · PRD §8.1 · FR-09 · US-05, US-09 · QA-05

- AC1: Given a new claim, material visual change, changed master, metadata, account or schedule, when saved, then the affected gate approvals reopen and execution waits for current approval.

#### R-43 Agents never approve
Must · R1 · PRD §3, §8.1, §14.1 · FR-09

- AC1: Given an agent or service identity, when it attempts to record an approval or a public action, then it is refused.

#### R-44 Production state machine
Must · R1 · PRD §8.2 · FR-08

- AC1: Given a project, when it progresses, then it uses DRAFT, RESEARCHING, SCRIPT_REVIEW, STORYBOARD_REVIEW, PRODUCING, QA, FINAL_REVIEW and APPROVED_EXPORT, with BLOCKED, FAILED, REVISION_REQUIRED and CANCELLED; illegal transitions are refused.

### F-13 Package, export and manual publication

#### R-45 Publication bundle
Must · R1 · PRD §10.3 · FR-23 · US-13

- AC1: Given an approved package, when exported, then the bundle contains master, captions, script, metadata, original cover, description with reviewed attribution, rights, versions and costs.

#### R-46 Export is not publication
Must · R1 · PRD §8.2 · FR-24 · US-12, US-13

- AC1: Given an exported bundle, when downloaded, then the publication state is "awaiting manual upload" and it never counts as published.

#### R-47 Manual publication record
Must · R2 · PRD §8.2, §16 · FR-24 · US-13, US-19 · QA-09

- AC1: Given a manual upload, when the operator records it, then actual account, external ID, URL, time, observed visibility, verification result (NOT_CHECKED, PASSED, PARTIAL, FAILED) and evidence are stored and labelled manual.
- AC2: Given a public URL whose package differs from the approved one, when recorded, then the mismatch is flagged.

#### R-48 Publication state per platform and account
Must · R2 (manual states); Should · R3 (connected states) · PRD §8.2 · FR-24, FR-15

- AC1: Given a package, when it is published to each platform and account, then state is tracked separately using the PRD §8.2 states, with provider processing status and last-checked time stored independently.

#### R-49 Post-publication corrections
Must · R2 · PRD §8.2, §16 · FR-07 · J6

- AC1: Given a factual problem in published content, when found, then it is surfaced with a proposed repair plan; nothing is deleted or replaced externally without a new approval.

### F-14 Runs, recovery and cancellation

#### R-50 Run and attempt records
Must · R1 · PRD §15 · FR-08 · US-14

- AC1: Given any task, when it runs, then run, task and attempt IDs, state, prompt, model and tool versions, failure reason, retries and spend are inspectable.

#### R-51 Bounded retry, timeout and resume
Must · R1 · PRD §14.2, §20 · FR-28 · US-14 · QA-06

- AC1: Given a worker crash, duplicate delivery or provider timeout, when the run resumes, then compatible completed work and current approvals survive, and retries stop at the task's ceiling.
- AC2: Given a failed step, when the operator chooses manual takeover, then the run records it and continues from that step.

#### R-52 Cancellation and reconciliation
Must · R1 · PRD §8.1, §16 · FR-28 · US-14 · QA-06, QA-07

- AC1: Given a cancel, when confirmed, then no further work is dispatched and reserved budget is released.
- AC2: Given an external write with unknown outcome, when recovery runs, then it reconciles the recorded state before any new write.

#### R-53 Actionable errors
Must · R1 · PRD §13, §20 · FR-28

- AC1: Given an error, when shown, then it names the scene, object, claim or account, classifies it (retryable provider failure, invalid content, deterministic render defect, uncertain public action) and offers the matching repair option.

### F-15 Provenance, rights and data control

#### R-54 Provenance per output
Must · R1 · PRD §15 · FR-10 · QA-08

- AC1: Given any output, when inspected, then its sources, licences, prompt, spec, model and tool versions and approvals are linked.

#### R-55 Rights ledger
Must · R1 · PRD §5.2, §15 · FR-10 · QA-08

- AC1: Given an asset, voice, font or music file, when registered, then origin, hash, licence and expiry are recorded.
- AC2: Given an unlicensed or expired asset, when used in a package, then approval is blocked.

#### R-56 Data export
Must · R1 · PRD §20 · FR-10 · US-26

- AC1: Given a project, when the owner exports it, then permitted records and artifacts are produced in an open format.

### F-16 Editorial series and content policy

#### R-57 Series and narrative structures
Must · R1 · PRD §5.1 · CR-01 · US-21

- AC1: Given a brief, when created, then it is tagged with one of What If, Wait How Does That Work, Solve This or Inside the Machine, and the script task uses that series' narrative structure.

#### R-58 Series slate tracking
Must · R2 · PRD §5.1, §6.5 · CR-01 · US-21

- AC1: Given the validation slate, when viewed, then planned versus approved versus published counts per series are shown against the 4/4/2/2 allocation, and each episode keeps its own costs, approvals and release.

#### R-59 Content policy review
Must · R1 · PRD §5.1, §5.2 · CR-03

- AC1: Given Gate B or D, when reviewed, then a checklist confirms no impersonation, fabricated sources or events, deceptive editing, or unverified health or financial claims stated as fact; a failure blocks approval.

#### R-60 AI-production disclosure
Must · R2 · PRD §5.2, §16, ref S7 · CR-03

- AC1: Given a package, when approved, then the voluntary AI-production identity is applied and the platform-native disclosure assessment for the actual media is recorded.

### F-17 Studio and agent tasks

#### R-61 Studio surfaces with structured controls
Must · R1 · PRD §13 · FR-02–FR-09 · US-02–US-14 · QA-09

- AC1: Given R1, when the operator works, then Projects and briefs, Script and evidence, Storyboard and preview, Revision impact, Package and export, and Runs and recovery are available with structured controls for every consequential action; Publication record is added at R2.
- AC2: Given progress, spend or a block, when shown, then estimated and actual spend and blocked states are visible, and unavailable data is shown as unavailable, never as empty success.
- AC3: Given P01, when making several distinct videos at R1, then no normal-use step requires a code edit.

#### R-62 Basic asset and brand library
Must · R1 (basic) · PRD §13 · FR-01, FR-10

- AC1: Given approved reusable objects and assets, when browsed, then each shows licence and version history.

#### R-63 Bounded model task contracts
Must · R1 · PRD §14.1 · FR-03, FR-04 · QA-01

- AC1: Given research, script and storyboard tasks, when defined, then each has an input, output schema, permitted tools, budget, retry ceiling, failure states and evaluation fixtures; no other autonomous agent runtime exists at R1.

#### R-64 Chat-driven drafting
Could · R1+ · PRD §13

- AC1: Given chat, when it is used, then it can only create or revise drafts; structured controls remain the way to inspect state and take consequential actions.

#### R-65 Model critique in QA
Could · R1+ · PRD §14.1

- AC1: Given deterministic checks, when model critique is enabled, then it adds findings but never replaces human review or approves.

### F-18 Channel connection (R3)

#### R-66 YouTube channel connection
Should · R3 · PRD §7.1, §16 · FR-11, FR-15 · US-15, US-26 · QA-10

- AC1: Given an OAuth connection, when completed, then the actual account identity, scopes and an account-specific capability preflight are recorded and shown.
- AC2: Given analytics permission only, when publishing is attempted, then it is refused; given revocation, then stored credentials cannot be reused.

#### R-67 Instagram eligibility
Should · R3 · PRD §16, ref S8–S9 · FR-12 · US-15

- AC1: Given an Instagram account, when connected, then only verified eligible capabilities are enabled, missing scopes are shown and export remains the fallback.

### F-19 Connected publishing (R3)

#### R-68 Private transfer and readiness
Should · R3 · PRD §16, ref S1–S4 · FR-25 · US-17 · QA-07

- AC1: Given an approved package, when uploaded to YouTube, then private visibility is set explicitly (never an omitted default), the resumable session and external ID are stored securely and processing and readiness checks are recorded.

#### R-69 Release and reconciliation
Should · R3 · PRD §8.2, §16 · FR-15 · US-17 · QA-07

- AC1: Given a current Gate E approval for this package, account and instruction, when release runs, then only that package is released.
- AC2: Given a lost acknowledgement, when recovering, then state becomes PUBLICATION_UNKNOWN and is reconciled or verified by the operator before any new write.

#### R-70 Scheduling, cancellation and calendar
Should · R3 · PRD §13, §16 · FR-26 · US-18 · QA-05

- AC1: Given a schedule, when set, then the local time is shown, past times are rejected and changed time or package needs a new approval.
- AC2: Given a cancellation, when requested, then it stays pending until the platform confirms or is marked unknown, and conflicting releases are blocked meanwhile.

#### R-71 Connected publication verification
Should · R3 · PRD §8.2, §16 · FR-27 · US-19

- AC1: Given a release, when verified, then intended account, observed public status and metadata consistency are checked; unavailable playback checks produce PARTIAL with a reason.

### F-20 Audience learning and experiments (R3)

#### R-72 Metric snapshots and dictionary
Should · R3 · PRD §17.1 · FR-11, CR-06 · US-20 · QA-11

- AC1: Given a metric, when imported or entered manually, then its source, platform definition, API version, window, denominator, availability and import time are stored; manual entries are labelled manual.
- AC2: Given a missing, delayed, unsupported or permission-denied value, when displayed, then it is distinct from zero.

#### R-73 Content Opportunity Lab
Should · R3 · PRD §17.2 · FR-13, CR-05 · US-16

- AC1: Given candidates, when compared, then editable ratings, the weighted score (Σ weight × rating ÷ 5), rationale, evidence, uncertainty, effort and cost are shown; the score is labelled a heuristic, never a probability of virality.
- AC2: Given a high score, when a blocker exists, then the score does not bypass it.

#### R-74 Experiment tracking
Should · R3 · PRD §17.3 · FR-14 · US-20

- AC1: Given a publication, when the experiment is created before release, then question, hypothesis, treatment, primary metric, baseline or cold-start status, window and constraints persist, and observations and confounders are added later.

#### R-75 Diagnostic recommendations
Should · R3 · PRD §17.3 · CR-07 · US-20

- AC1: Given a recommendation, when shown, then it cites its observations, alternatives and uncertainty, and is a proposal the operator accepts or rejects; it never authorises spend or publication.

#### R-76 Reach is not people
Should · R3 · PRD §17.1, §18 · CR-09

- AC1: Given cross-platform views, when summed, then they are never presented as deduplicated people.

#### R-77 Conditional growth study tracking
Should · R3 (after the R2 gate) · PRD §18 · CR-08

- AC1: Given the study, when tracked, then the twelve qualification videos are excluded, planned versus actual originals (up to 48) and uploads (up to 96) are distinct, and late follow-up windows are reported as follow-up.

### F-21 Customer and business expansion (Won't for this baseline)

#### R-78 Customer workspaces, roles, onboarding, quotas and billing
Won't · R4 · PRD §2.1, §6.9 · FR-16 · US-22, US-23 · QA-10 — PRD evidence: tenant isolation, onboarding, quotas and billing verified before paid beta.

#### R-79 Recurring proposals
Won't · R4 · PRD §11 · FR-17 — PRD evidence: scheduled suggestions respect current review, budget and publication rules.

#### R-80 Customer brand and series variants
Won't · R4 · PRD §12 · CR-10 · US-21 (customer part) — PRD evidence: workspace ownership, brand separation and cost limits verified.

#### R-81 Maintained technical explanations (P05 pilot)
Won't · R4 · PRD §6.10 · US-24 · J8 — reuses R-31–R-33; automatic enterprise knowledge sync excluded.

#### R-82 Business conversion objectives
Won't · R5 · PRD §6.7 · FR-18 · US-25 · J5 — PRD evidence: permissioned first-party outcomes separated from engagement and unattributed action.

## Non-functional requirements (NFR-xx)

#### NFR-01 Reliability
Must · R1 · PRD §14.2, §20 · FR-28 · QA-06

- AC1: Given a worker restart, duplicate delivery or unknown external outcome, when the run continues, then internal writes are idempotent, retries and timeouts are bounded and external uncertainty is reported, never assumed successful.

#### NFR-02 Performance
Must · R0 (baseline) · PRD §20

- AC1: Given R0, when the first sample is produced, then draft-preview and final-render times and resource use are measured and recorded as the baseline; no speed is promised before that (targets: Q-15).

#### NFR-03 Reproducibility
Must · R1 · PRD §9.3, §20

- AC1: Given pinned inputs, fonts, renderer and tool versions and seeds, when a fixture is re-rendered, then output matches within documented tolerance and differences are explainable.

#### NFR-04 Access control
Must · R1 · PRD §20 · FR-29 · QA-10

- AC1: Given any record, artifact, job, export or support tool, when accessed, then authentication, workspace ownership and least privilege are enforced, and media is reachable only through short-lived signed access.

#### NFR-05 Untrusted inputs and no generated-code execution
Must · R0 · PRD §9.1, §19.2, §20 · FR-05 · QA-08

- AC1: Given model output, source pages or assets, when processed, then they are data only: no LLM-generated or source-page code or instructions are executed; the compiler accepts only bounded typed data.
- AC2: Given a fetch, when requested, then private-network and metadata-service addresses are refused, downloads are size-bounded and file types are validated.
- AC3: Given the prompt-injection red-team fixtures, when tasks run, then injected instructions cause no tool call or state change outside the task contract.

#### NFR-06 Credentials and secrets
Must · R1 · PRD §20 · FR-29 · QA-10

- AC1: Given platform credentials and transfer-session URLs, when stored or logged, then they are encrypted at rest, restricted and redacted from logs; no secret is in the repo.

#### NFR-07 Bounded spend
Must · R1 · PRD §20, §21.1 · FR-08 · QA-06

- AC1: Given concurrent dispatch, retries or cancellation, when spend is reconciled, then total spend never exceeds the reserved allowance (R-34) and no repair loop is unbounded.

#### NFR-08 Accessibility
Must · R0 · PRD §2.2, §5.2, §20

- AC1: Given a video, when reviewed at phone size and muted, then captions are accurate, text and notation meet the adopted contrast standard (Q-17), safe zones hold and motion does not flash.

#### NFR-09 Observability
Must · R1 · PRD §14.2, §20

- AC1: Given a run, when traced, then run, task, attempt, content and artifact IDs, costs and failures are linked so the operator can explain an output and recover a failed step.

#### NFR-10 Data governance
Must · R1 (R3 for revocation) · PRD §15, §20 · FR-29 · US-26 · QA-12

- AC1: Given retention rules (Q-14), when applied, then superseded artifacts are kept or removed accordingly, including cached copies, while everything needed to explain a publication is kept.
- AC2: Given a deletion request, when executed, then supported stores and caches are cleared and the system does not claim to remove external public posts; access is audited.

#### NFR-11 Portability
Must · R1 · PRD §14.2, §15, §20

- AC1: Given content and scene contracts, when a model, TTS or renderer provider changes, then contracts are unaffected and adapters pass shared fixtures.

#### NFR-12 Resource isolation
Must · R1 · PRD §20

- AC1: Given a render job, when it runs, then CPU, memory, time, object counts and asset sizes are bounded and limit breaches fail cleanly.

#### NFR-13 Deployability
Must · R1 · PRD §14.2, §20

- AC1: Given a fresh clone, when set up, then local and staging environments are reproducible, credentials are separate per environment and migrations are reviewed with a tested rollback.

#### NFR-14 Backup and restore
Must · R1 · PRD §20 · QA-12

- AC1: Given backups, when a representative restore is rehearsed, then content, manifests and run references are recovered within the adopted RPO/RTO (Q-16).

#### NFR-15 Operational monitoring
Must · R1 · PRD §20 · QA-12

- AC1: Given operation, when monitored, then stuck runs, queue delay, render duration and memory, provider errors, retry spend, failed approvals, publication uncertainty and cost per approved output are visible and alert.

#### NFR-16 Output format and language scope
Must · R0 · PRD §4

- AC1: Given R1 scope, when producing, then output is English, one licensed narrator, 9:16 at 1080×1920 and 30 fps, 30–60 s primary length, with the engine accepting 30–90 s.

#### NFR-17 AI task quality and evaluation
Must · R1 · PRD §19.2

- AC1: Given research, script and storyboard tasks, when evaluated, then the corpus covers all four series, conflicting and unsupported sources, long narration and labels, invalid specs, prompt injection, unsafe asset URLs and revision cases, and prompt, model and tool versions, inputs, outputs, reviewer judgement and costs are persisted.

#### NFR-18 Platform policy compliance
Must · R2 · PRD §5.2, §16, ref S6–S7

- AC1: Given a missing platform API, when a capability is needed, then the product shows it as unavailable and offers export; it never substitutes scraping or browser automation.

#### NFR-19 Single canonical schema
Must · R0 · PRD §15

- AC1: Given contracts, when built, then JSON Schema and TypeScript types are generated from one canonical schema source and both runtimes pass the same valid and invalid fixtures; schema versions are pinned and migrated deliberately.

## KPIs (KPI-xx)

Analytics events for each KPI are defined in `OBSERVABILITY.md` (Stage 2). A target marked "Q-xx" is open.

| KPI | Measure | Target | How measured | Release | PRD source |
|---|---|---|---|---|---|
| KPI-01 | Validation slate completed | 12 approved original public videos, 4/4/2/2 across the series | R-58 slate view; publication records (R-47) | R2 | §12 CR-01, §19.3 |
| KPI-02 | Production reliability | Proposed ≥ 10 of 12 completed without code-level repair; exact rate and all manual work reported (Q-04) | Run records (R-50) tagged code-repair or manual | R2 | §19.3 |
| KPI-03 | Editorial quality | Proposed: every rubric dimension ≥ 4/5, zero unresolved material errors, zero rights blockers per approved video (Q-04) | Rubric on final master (R-38) | R1 | §19.1 |
| KPI-04 | Human effort per approved video | Lower than a documented manual baseline at equal or better quality (baseline: Q-13) | Active minutes (R-36) vs baseline | R2 | §19.3, §21.1 |
| KPI-05 | Variable cost per approved output | At or below the per-video ceiling (Q-05) | Cost records incl. failed attempts (R-35) ÷ approved outputs | R1 | §21.1 |
| KPI-06 | Primary audience metric | Chosen available attention measure, 7-day window proposal, cold-start labelled; no numeric target before a baseline (Q-09) | Manual entry at R2; import at R3 (R-72) | R2 manual, R3 | §10.3, §17.3 |
| KPI-07 | Opening signal (initial choice / stayed to watch) | Diagnostic, no target | R-72, where the endpoint supports it | R3 | §17.1 |
| KPI-08 | Attention depth (average duration, % viewed, retention) | Diagnostic, compared within duration groups | R-72 | R3 | §17.1 |
| KPI-09 | Payoff signal (completion, replay) | Diagnostic | R-72 | R3 | §17.1 |
| KPI-10 | Shares and saves per eligible reach | Diagnostic, actual supported denominator | R-72 | R3 | §17.1 |
| KPI-11 | Series interest (subscribers, returning audience) | Diagnostic, needs history | R-72 | R3 | §17.1 |
| KPI-12 | Recommendation usefulness | Repeatedly better than a simple editorial baseline before any optimisation claim | R-75 proposals vs baseline decisions over the study | R3 | §17.3, §19.3 |
| KPI-13 | Growth study reach | Stretch: 1,000,000 cumulative platform-reported organic views across experiment uploads in the defined window; not unique people | R-77; summed per upload | R3, conditional | §18 |
| KPI-14 | Comprehension and readability | Muted-with-captions review passes for every approved video; viewer comprehension method: Q-19 | Rubric item (R-38); feedback where available | R2 | §2.2, §10.3, §19.1 |

### KPIs and the moat hypotheses

The moat hypotheses are owned by PRD §1.1; this table says which KPIs test each. None is claimed before its proof is met.

| Moat hypothesis (PRD §1.1) | Earned at | Tested by |
|---|---|---|
| 1 Typed scene library and compiler | R0–R1 | KPI-03 editorial quality and KPI-02 production reliability across the slate (KPI-01) |
| 2 Trust | R1–R2 | KPI-03 (no material errors or rights blockers); repeat use by R4 pilots (out of scope here) |
| 3 Cheap targeted revision | R1 | KPI-04 human effort and KPI-05 cost per approved output, revisions included |
| 4 Learning loop | R3 onward | KPI-12 recommendation usefulness; KPI-06 records the first hypotheses from R2 |

R4 commercial measures (paid conversion, weekly active workspaces, margin, retention; PRD §21.2) are out of scope.

## Out of scope

From PRD §3 non-goals, R4/R5 scope and the project's hard limits:

- Universal video editor or professional multi-track timeline editor (§3, §13).
- Arbitrary prompt-to-video generation for every topic (§3).
- Fully unattended public publishing; blanket publishing permission from a connection or approval (§3).
- Paid advertising, CRM connectors, conversion attribution and business outcome tracking (§3; R-82).
- Private-data scraping, and browser automation in place of a missing API (§3, §16).
- Foundational model training (§3, §14.2).
- Long-form production as a first-class workflow (§3).
- Agent marketplace; more than the three bounded model tasks at launch (§3, §14.1).
- Billing, customer workspaces, team roles, agency administration (§3; R-78–R-80).
- Multilingual narration or dubbing (§3, §4).
- Extensive generative video; generative illustrations beyond a budget-capped option (§3, §21.1).
- Content repurposing (§3).
- Automatic enterprise knowledge synchronisation (§6.10).
- Commercial pricing, subscription and licensing the library as an API (§21.2).
- Kubernetes, microservice fleets and a Rust migration for launch (§14.2).

## Coverage (PRD section → requirements)

"Input to" marks a section that holds no product requirement; its content is used in the named Stage 2–3 doc instead.

| PRD section | Covered by |
|---|---|
| §1 Product summary | R-06, R-61; four layers mapped to F-06 (engine), F-17 (Studio), F-20 (audience), F-21 (business, Won't) |
| §1.1 What it solves and defensibility | No new R-xx: strategy, not behaviour. Tested by KPI-01–KPI-06, KPI-12, KPI-14 ([KPIs and the moat hypotheses](#kpis-and-the-moat-hypotheses)); Q-32 |
| §2 Problem and users | R-01, R-05; out of scope: generic unlimited video users |
| §2.1 Personas P01–P06 | P01/P02 → F-01–F-17; P03/P04 → R-78, R-80; P05 → R-81; P06 → R-82 |
| §2.2 Viewer profile | NFR-08, KPI-14, R-27 |
| §2.3 Roles and authority | R-05, R-43 |
| §2.4 Persona validation | Input to DELIVERY_PLAN.md (validation activities); Q-13 |
| §3 Principles and boundaries | R-43, R-05; Out of scope list |
| §4 Releases and priorities | Conventions; NFR-16; KPI table; Q-18 |
| §5 Content strategy | R-57, R-59 |
| §5.1 Editorial portfolio | R-57, R-58, R-39, R-13 |
| §5.2 Visual and narrative | R-23, R-20, R-27, R-59, R-60, R-55, NFR-08 |
| §6.1 User stories US-01–26 | See "User story trace" below |
| §6.2–6.10 Journeys J1–J8 | Features table (Journeys column) |
| §6.11 Story validation | Input to TEST_STRATEGY.md (story walkthroughs, QA-09) |
| §7.1 Channel setup | R-04, R-66 |
| §7.2 Production stages 1–16 | 1–2 R-06; 3 R-08, R-11; 4 R-14; 5 R-16; 6 R-07, R-34; 7 R-25, R-26; 8 R-28; 9 R-31; 10 R-29, R-30; 11 R-40, R-45; 12 R-46, R-68; 13 R-68; 14 R-69, R-70; 15 R-47, R-71; 16 R-36, R-72 |
| §8.1 Human review gates | R-40–R-43 |
| §8.2 State and verification | R-44, R-46–R-49 |
| §9.1 Library boundaries | R-18, R-19, R-24, NFR-05 |
| §9.2 Objects and timing | R-11, R-12, R-20–R-22, R-26 |
| §9.3 Rendering and revision | R-30–R-32, NFR-03 |
| §10 Reference storyboard | R-11 AC2, R-31 AC2, R-23; input to UI_DESIGN.md and PRD M1 fixtures |
| §11 FR-01–30 | See "FR and CR trace" below |
| §12 CR-01–10 | See "FR and CR trace" below |
| §13 Studio experience | R-61, R-62, R-64, R-53, R-70 |
| §14.1 Agent tasks | R-63, R-65, R-08, R-14, R-16 |
| §14.2 Implementation baseline | NFR-01, NFR-11, NFR-13; stack choices: input to ADRs and TECH_STACK.md (Q-06, Q-07, Q-21, Q-22) |
| §15 Data and contracts | R-06, R-08, R-30, R-50, R-54, NFR-19; input to docs/contracts/ |
| §16 Publishing and integrations | R-47, R-49, R-66–R-71, NFR-18 |
| §17.1 Measurement dictionary | R-72, R-76, KPI-07–KPI-11 |
| §17.2 Opportunity Lab | R-73 |
| §17.3 Experiment method | R-74, R-75, KPI-06, KPI-12 |
| §18 Growth experiment | R-77, KPI-13 |
| §19.1 Editorial rubric | R-38, KPI-03, KPI-14 |
| §19.2 Verification matrix QA-01–12 | Trace lines on each R/NFR; input to TEST_STRATEGY.md |
| §19.3 Release gates | KPI-01, KPI-02, KPI-04; input to DELIVERY_PLAN.md |
| §20 NFR and operations | NFR-01–NFR-15 |
| §21.1 Production economics | R-34–R-36, KPI-05 |
| §21.2 Commercial validation | Out of scope (R4) |
| §22 Roadmap and effort | Input to DELIVERY_PLAN.md (Q-03) |
| §23 Workstreams | Input to DEVELOPMENT_PLAN.md |
| §24 OOS-001–027 | Input to SPEC-xx in DEVELOPMENT_PLAN.md |
| §25 Risks | Input to DELIVERY_PLAN.md (RAID) |
| §26 DEC-01–12 | QUESTIONS.md Q-01–Q-12 |
| §27 Sources and references | Informative; ref S1–S14 cited from R-66–R-68, R-60, Q-07 |

### FR and CR trace

| PRD ID | Requirements |
|---|---|
| FR-01 | R-01, R-02, R-23, R-62 |
| FR-02 | R-04, R-06 |
| FR-03 | R-08, R-09, R-10 |
| FR-04 | R-14, R-16, R-17 |
| FR-05 | R-18, R-19, R-21 |
| FR-06 | R-25, R-27, R-28, R-29 |
| FR-07 | R-31, R-32, R-33, R-49 |
| FR-08 | R-35, R-44, R-50, NFR-07 |
| FR-09 | R-05, R-40, R-41, R-42, R-43 |
| FR-10 | R-10, R-30, R-54, R-55, R-56 |
| FR-11 | R-66, R-72 |
| FR-12 | R-67 |
| FR-13 | R-73 |
| FR-14 | R-74 |
| FR-15 | R-48, R-69 |
| FR-16 | R-78 |
| FR-17 | R-79 |
| FR-18 | R-82 |
| FR-19 | R-20, R-22 |
| FR-20 | R-11, R-12 |
| FR-21 | R-21, R-26 |
| FR-22 | R-07, R-34 |
| FR-23 | R-45 |
| FR-24 | R-46, R-47, R-48 |
| FR-25 | R-68 |
| FR-26 | R-70 |
| FR-27 | R-71 |
| FR-28 | R-51, R-52, R-53, NFR-01 |
| FR-29 | R-01, NFR-04, NFR-06, NFR-10 |
| FR-30 | R-36 |
| CR-01 | R-57, R-58, KPI-01 |
| CR-02 | R-15 |
| CR-03 | R-09, R-12, R-13, R-37, R-38, R-59, R-60 |
| CR-04 | R-39 |
| CR-05 | R-73 |
| CR-06 | R-72 |
| CR-07 | R-75 |
| CR-08 | R-77, KPI-13 |
| CR-09 | R-76 |
| CR-10 | R-80 |

### User story trace

| Story | Requirements | Story | Requirements |
|---|---|---|---|
| US-01 | R-01, R-02, R-03, R-04 | US-14 | R-50, R-51, R-52 |
| US-02 | R-06, R-07 | US-15 | R-66, R-67 |
| US-03 | R-08, R-09, R-10 | US-16 | R-73 |
| US-04 | R-11, R-12, R-13 | US-17 | R-68, R-69 |
| US-05 | R-14, R-15, R-17, R-42 | US-18 | R-70 |
| US-06 | R-16, R-17, R-18, R-20 | US-19 | R-47 (manual), R-71 |
| US-07 | R-03, R-25, R-26 | US-20 | R-72, R-74, R-75 |
| US-08 | R-28, R-29 | US-21 | R-39, R-57, R-58; R-80 (customer) |
| US-09 | R-31, R-32, R-33, R-42 | US-22 | R-78 |
| US-10 | R-34, R-35 | US-23 | R-78 |
| US-11 | R-09, R-33, R-37, R-38 | US-24 | R-81 |
| US-12 | R-05, R-41, R-46 | US-25 | R-82 |
| US-13 | R-45, R-46, R-47 | US-26 | R-56, NFR-10; R-66 (revocation); R-78 (customer) |
