# OpportunityOS Product Requirements Document

**Version:** 2.0  
**Revision:** Persona and user story expansion on 12 November 2026  
**Date:** 12 November 2026  
**Status:** Final consolidated draft for product and engineering planning  
**Product:** Audience intelligence and original animated video production  
**Initial validation:** One owned educational channel, with YouTube first and Instagram distribution where eligible  
**Intended readers:** Product, editorial, design, engineering and operations

This PRD defines the product, its required behavior, the complete idea-to-publication journey, and the evidence needed to expand it. It consolidates the supplied OpportunityOS v1 PDF, the Overall PRD v1.1, the updated Development Plan revision 1.1, and the visual storytelling requirements established through the user's examples. It replaces overlapping scope descriptions in those documents for subsequent planning. It does not record budget approval, completed integrations, implementation results or paid demand.

The first investment is a small production system that can explain an idea through original animation, revise it reliably, and publish an approved version on the correct channel. Broader analytics, paid workspaces and business workflows follow separate validation gates. Requirements use “must”; implementation choices and unvalidated targets are explicitly identified. The open decisions in Section 26 must be resolved at their stated gates.

## Contents

1. Product summary
2. Problem target users and personas
3. Product principles and boundaries
4. Releases and priority definitions
5. Content strategy and visual identity
6. User stories and journeys
7. Complete production lifecycle
8. Approval and publication governance
9. Signal Motion Engine
10. Original reference storyboard
11. Functional requirements
12. Content and experiment requirements
13. Studio experience
14. Agent tasks and workflow architecture
15. Data and interface contracts
16. Publishing and platform integrations
17. Audience intelligence and experimentation
18. Conditional growth experiment
19. Quality and release acceptance
20. Nonfunctional requirements and operations
21. Costs and commercialization
22. Roadmap and effort assumptions
23. Workstreams and ownership
24. Engineering handoff backlog
25. Risks and responses
26. Open decisions and change control
27. Source consolidation and references

## 1 Product summary

OpportunityOS turns a viewer question into an original animated explanation and a measurable content experiment. It helps an operator select ideas, establish evidence, write a story, compose precise animation, review the result, publish with permission, and learn from available channel data.

Its production style makes the explanation visible. Numbers, shapes, diagrams and other meaningful objects persist through a sequence of demonstrations and transformations. Narration and captions follow the same events. The video resolves the question it opens with and leaves the viewer with an understandable insight.

The product has four layers:

| Layer | Purpose | Initial commitment |
|---|---|---|
| Signal Motion Engine | Original brand system, scene grammar, animation components, audio timing, rendering and quality checks | Foundation of the first release |
| Creator Studio | Briefs, sources, scripts, storyboards, preview, targeted revisions, approvals and distribution records | Internal operator application |
| Audience Intelligence | Authorized channel metrics, content opportunities, experiments and evidence-linked learning | After production is useful and measurable |
| Business OpportunityOS | Connect content and authorized actions to first-party commercial outcomes | Conditional future investment |

The central record is the **Content Opportunity Contract**. Earlier drafts also called this the Audience Opportunity Contract; they refer to the same concept. The contract connects the audience need, hypothesis, evidence, creative plan, budget and approvals to the final artifact, publication and observed outcome.

The business hypothesis is that established creators and studios will pay for repeatable original production with less effort and clearer learning than their current workflow. Own-channel reach can validate content interest; it does not establish customer willingness to pay or a defensible competitive advantage.

## 2 Problem target users and personas

Creators still coordinate research, scripting, animation, narration, editing, revision, distribution and analytics across several tools. Faster drafting does not by itself ensure factual accuracy, visual clarity, originality, consistent branding or useful audience learning. New channels have little evidence to guide topic choices. Small businesses face the additional difficulty of connecting content attention to actual enquiries, bookings or purchases.

| User | Job to be done | Evidence of value |
|---|---|---|
| Internal channel operator | Produce and improve original educational Shorts with controlled effort and cost | Completed approved videos, measured human time and usable learning |
| Established educational creator | Maintain original production without recurring editing and research bottlenecks | Weekly repeat production and lower effort at equal or better quality |
| Specialist content studio | Produce consistent client or owned-channel series with dependable revisions and approvals | Reliable recurring use, brand separation and manageable support |
| Technical educator or B2B education team | Explain approved technical knowledge clearly | Accurate demonstrations and maintainable content |
| Small service business later | Use useful content to support qualified attention and commercial action | Permissioned first-party outcomes with attribution limits |

The internal operator initially performs editorial, factual, brand and publication review. A specialist must review claims the operator cannot credibly verify. The product will not optimize for users seeking unlimited generic videos with no review or guaranteed viral results.

### 2.1 Persona definitions

These are design personas derived from the product scope, not validated interview findings. They describe work and decisions without invented demographics, customer quotations or purchase commitments. Persona IDs identify a user need; permissions separately determine who may perform an action.

**P01 Internal channel operator** is the primary R1–R3 user. This person operates the owned educational channel, combining topic selection, production review, publishing and learning within limited engineering/editorial capacity. Their job is to turn a worthwhile idea into an original visual story without repeatedly repairing code or coordinating disconnected tools. Their difficulties are inconsistent animation, fragmented evidence, slow revisions and unknown costs. They need a clear production queue, editable scripts/scenes, visible blockers, dependable export and honest channel status. They approve only within configured ownership/budget scope and seek specialist review outside their expertise. Success means accepted videos with measured effort/cost, fewer engineering repairs and a useful next editorial decision. R0 may still require technical assistance.

**P02 Editorial and subject reviewer** supports R1 onward. This person checks whether claims, calculations and visuals agree, sources support the explanation, and the opening promise is fulfilled. They may be the internal operator or a separate specialist. Their difficulty is finding the precise issue without reading execution logs. They need side-by-side evidence, narration and preview, unresolved-claim flags, version comparisons and targeted revision requests. They approve or return content only within assigned review scope; this does not grant account credentials or publishing authority. Success means no unresolved material errors/rights blockers in approved work and efficient re-review of changed content.

**P03 Established educational creator** is a potential R4 buyer and repeat operator. This creator already has a recognizable voice, an audience and a recurring workflow. Their job is to sustain original output with less research, animation and revision effort. They are concerned about generic output, lost editorial control, opaque generation and unpredictable charges. They need their own brand context, exportable artifacts, transparent usage, reversible drafts and available channel evidence. Subscription purchase never grants blanket publishing permission. Adoption requires measured quality/effort improvement in their real workflow followed by repeat paid use. Audience size, budget and willingness to pay remain discovery questions.

**P04 Specialist content studio lead** is a potential R4 buyer and workspace administrator. This person coordinates editors, reviewers and publishers across owned/client projects. Their job is consistent delivery with controlled revisions and clear sign-off. Main risks are cross-client asset use, unclear approvals and hidden spend. They need scoped brands/projects, assigned roles, approval history, usage limits and inspectable deliverables. Administration does not grant every member public-release authority. Success is repeat production with correct brand/client separation and manageable revisions/support. This persona does not add broad agency administration or unrestricted client-channel management to R1.

**P05 Technical educator or product education lead** is a potential R4 pilot user. This person turns approved mathematics, science or product knowledge into understandable explanations and maintains them when knowledge changes. Their difficulty is visually plausible animation that changes the meaning or retains stale claims/narration after revision. They need reviewed derivations/sources, verified models, semantic object mapping and version-aware changes. They approve domain correctness within their expertise; public release still requires a publisher. Success is accurate demonstrations, useful learner feedback and maintainable versions. Approved uploaded/entered knowledge is sufficient; automatic enterprise knowledge synchronization is not implied.

**P06 Small business owner** is a future R5 buyer/user. This person wants useful content to support a specific outcome such as qualified enquiries or bookings while focusing on running the business. They struggle to distinguish attention from commercial value and cannot supervise an open-ended marketing agent. They need a narrow goal, approved facts, bounded spend, simple decisions and permissioned outcome reporting. Content releases, campaigns and other actions have separate authority. Success is credible utility against the chosen objective with attribution limits and operating costs visible. Ads, CRM and conversion connectors remain outside launch scope.

### 2.2 Viewer profile

The downstream beneficiary is a curious beginner watching on a phone, potentially with audio muted and little prior context. This is a design scenario rather than a measured audience claim. The viewer should quickly understand the question, track persistent objects, read captions/notation and receive the promised explanation. Viewers are not Studio account roles. Test comprehension/readability directly where possible; retention alone does not establish learning.

### 2.3 Roles and authority

| Role | Responsibility within scope | Authority boundary |
|---|---|---|
| Owner or administrator | Configure workspace, access, budget and connections | Administration is not approval of every public action |
| Editor or operator | Draft briefs, scripts, scenes and revisions | Cannot bypass review or obtain unauthorized account access |
| Reviewer | Assess assigned claims, visuals, rights and versions | Sign-off does not grant publishing or billing control |
| Publisher | Release the approved package on an authorized account/time | Cannot silently change package, account or release instruction |
| Analyst | Inspect permitted results and propose experiments | Analysis does not authorize spend or publication |

One authenticated owner may hold several responsibilities in R1. Distinct customer team-role management completes at R4; basic ownership and approval scope are required from the internal release. Agents execute tasks and are not human personas or approval identities.

### 2.4 Persona validation

Validate P01/P02 through observed internal production/review sessions. Before paid expansion, inspect potential P03–P05 users' actual recent workflows and record effort, revision pain, purchase authority, quality requirements and willingness to pay. Validate P06 when selecting the R5 vertical. Update personas from evidence without presenting commercial assumptions as demonstrated behavior.

## 3 Product principles and boundaries

AI proposes and composes; deterministic software validates and executes; people approve consequential actions; recorded outcomes inform the next experiment. This principle applies to research, animation, budgets and public publication.

The product must preserve evidence, uncertainty and inspectability. Operators can inspect sources, scripts, scenes, costs, revisions and approvals. Quality and a satisfying explanation take precedence over publishing volume. Brand consistency must coexist with distinct stories, demonstrations and examples.

Initial non-goals are a universal video editor; arbitrary prompt-to-video generation for every topic; fully unattended public publishing; paid advertising; private-data scraping; foundational model training; long-form production as a first-class workflow; and an agent marketplace. Billing, customer workspaces, multilingual dubbing, extensive generative video, content repurposing, CRM connectors and conversion attribution belong to later scope.

The long-term ambition is broad automation with bounded authority. Early releases automate production steps between review gates. A scheduled post may execute under its specific approved release instruction; connecting an account or approving a draft is not blanket permission to publish future videos.

## 4 Releases and priority definitions

| Release | Required outcome | Completion evidence |
|---|---|---|
| R0 Feasibility prototype | One original mathematical or scientific visual story using the initial animation families | Narrated 30–45 second sample, captions, verified demonstration and targeted revision |
| R1 Internal Studio | Operator completes research, script, storyboard, render, revision and approved export | Several distinct videos completed through the application without normal-use code edits |
| R2 Channel validation | Full four-series slate and approved public videos, with manual distribution allowed | Twelve originals with review, effort, cost, rights and publication records |
| R3 Closed-loop channel product | Authorized publishing where feasible, analytics, opportunity scoring and experiment learning | Prospective experiment traced through observation and a documented next proposal |
| R4 Paid creator beta | Secure customer workspaces, onboarding, roles, quotas, billing and support | At least three paid pilots and evidence of repeat use and viable economics |
| R5 Business expansion | One selected commercial vertical with permissioned conversion signals | Verified incremental utility beyond engagement and a separate business case |

**P0** covers internal production and its R2 validation. R0 proves a subset; R1 provides the technical operator journey; CR-01 and the twelve-video gate complete at R2. **P1** covers R3 audience feedback and connected distribution. **P2** covers R4 commercial creator capabilities. **P3** covers R5 business outcomes. Priority does not imply that every requirement must ship in the first prototype.

The first hosted scope is one authenticated workspace, one house brand, English narration, one licensed narrator, and 9:16 output at 1080×1920. Launch content is primarily 30–60 seconds; the engine should support the broader 30–90 second range as validated. The first feasibility story targets 30–45 seconds. Manual public uploads and manual analytics are valid launch paths when honestly labeled and recorded.

## 5 Content strategy and visual identity

The channel promise is “Fascinating things made understandable through original AI animation.” Mathematics, science, technology and adjacent curiosity fit this promise. AI systems are one content family, not a permanent restriction on the channel. The first mathematical prototype validates a visual production method rather than selecting the final market niche.

### 5.1 Editorial portfolio

| Series | Narrative structure | Twelve-video slate |
|---|---|---:|
| What If | Counterfactual premise, assumptions, mechanism, consequences and bounded conclusion | 4 |
| Wait How Does That Work | Familiar mystery, observation, visual mechanism and answer | 4 |
| Solve This | Fair puzzle or pattern, thinking interval, demonstration and resolution | 2 |
| Inside the Machine | Familiar action, invisible system, traced flow and takeaway | 2 |

The initial 4/4/2/2 allocation approximates the earlier 30/30/20/20 percent hypothesis. It is an experimental mix, not a permanent publishing mandate. Select briefs whose explanations can be represented accurately by supported components. Preserve exploration after promising results appear.

Candidate formats include what-if demonstrations, everyday mechanisms, visual puzzles, mathematical patterns, AI concepts, technology flows and data stories. Mind-bending science and business/economics stories require suitable expertise and source review. An illustrative animation must not be presented as a measured simulation or footage of a real event.

### 5.2 Visual and narrative requirements

The supplied Lingualin screenshots establish a reference: dark canvas, bright color-coded digits, mathematical notation, geometric arrangement and concise captions. OpportunityOS must create an original brand, script, composition and explanatory progression. The screenshots do not identify the reference creator's tools or exact motion timing.

The house style must define palette, type scale, equation typography, caption placement, safe zones, transitions, narration voice, pacing and a discreet brand cue. Color meanings persist across transformations and are reinforced with position, labels or highlighting. Signature elements must not obstruct the opening or explanation. Long intros and decorative motion that compete with comprehension are unsuitable.

Each story must provide a reason to care, advance the explanation visually, limit each beat to a comprehensible idea, fulfill its opening promise and end with a useful payoff. Objects may carry the story; fictional characters are optional. Exact source claims and visual simplifications are reviewed together. Captions, contrast, non-flashing motion and muted-view comprehension are part of quality acceptance.

Content must not impersonate individuals, fabricate sources or real events, use deceptive editing, or present unverified health/financial claims as established facts. Assets, music, voices, fonts and illustrations require appropriate recorded usage rights.

The channel uses a consistent voluntary AI-production identity and applies platform-native disclosures when required for the actual media. Stylized mathematical animation and realistic synthetic depictions require different disclosure assessments. Do not equate a visible AI brand cue with a claim that every video is universally fact checked.

## 6 User stories and journeys

Stories express user intent and observable acceptance. The FR/CR register remains the requirements authority; release labels prevent later personas from expanding launch scope. J1–J5 retain their earlier meanings. J6–J8 add revision/recovery, customer onboarding and maintained technical education. Section 7 remains the canonical production-stage definition and Section 8 owns approval rules.

### 6.1 User story catalogue

Each story names its persona, release, requirement links and acceptance criteria. R0 demonstrates selected production behavior with technical assistance; R1 requires the usable internal Studio. Later users reuse these capabilities only within eligible customer workspaces.

**US-01 Configure a workspace.** As P01, I want saved brand, narrator and project settings so that videos start consistently. R1; FR-01, FR-29; J1/J3/J7. Acceptance: Given an authenticated owner, project creation stores scoped settings and a pinned brand version. Other workspaces cannot access its assets; changing defaults does not mutate approved renders.

**US-02 Choose a feasible idea.** As P01, I want a viewer question, payoff, animation plan and cost allowance so that I can decide whether to produce it. R1; FR-02, FR-22; J1. Acceptance: An idea becomes an editable contract with audience, format, evidence plan and budget. Unsupported operations or essential gaps appear before paid dispatch.

**US-03 Review evidence.** As P02, I want claims linked to their supporting evidence so that I can evaluate the explanation. R1; FR-03, FR-10, CR-03; J1/J6/J8. Acceptance: Selecting a claim shows source/location and review state. Unsupported/contradictory claims block applicable approval until resolved, removed or accurately qualified.

**US-04 Verify a demonstration.** As P02 or P05, I want equations, counts, units and geometry checked so that plausible animation cannot hide an incorrect explanation. R1, sampled at R0; FR-20, CR-03; J1/J8. Acceptance: Reviewed inputs yield displayed results and settled geometry. Invalid domains or mismatches stop progression and identify the issue.

**US-05 Shape the narrative.** As P01, I want to edit the hook, explanation and takeaway so that the story fulfills its promise. R1; FR-04, CR-02, CR-04; J1/J3. Acceptance: Beats and claim references are editable before production. Approval records a script version; material narration/claim changes reopen relevant downstream review.

**US-06 Review visual actions.** As P01, I want a storyboard showing what objects do so that I can judge whether visuals teach the idea. R1, sampled at R0; FR-05, FR-19; J1/J8. Acceptance: Scenes expose objects, actions, timing and narration. Identity/meaning persists through movement; invalid actions identify the affected scene/object.

**US-07 Audition voice and captions.** As P01, I want pronunciation and pacing controls so that speech and animation align. R1, sampled at R0; FR-06, FR-21; J1/J6. Acceptance: Measured audio duration informs timing/readable caption segments. A changed voice take updates affected alignment rather than silently forcing unreadable or excessively accelerated delivery.

**US-08 Preview before the master.** As P01, I want an inexpensive draft so that I can catch problems before final rendering. R1; FR-06, FR-22; J1. Acceptance: Preview records its inputs and spend. Failed generation/layout issues are visible, and the final-quality master receives independent checks.

**US-09 Revise affected scenes.** As P01, I want a targeted edit with dependency impacts so that prior work is reused without stale visuals/timing. R1, sampled at R0; FR-07, FR-19, CR-02; J6/J8. Acceptance: Impact review identifies rebuilt/reused artifacts and cost. Duration/state changes propagate; earlier approved masters remain in history.

**US-10 Control spend.** As P01, I want estimated/actual costs and an enforced allowance so that concurrent work or retries cannot spend indefinitely. R1; FR-08, FR-22, FR-30; J1/J6. Acceptance: Dispatch reserves available budget and pauses when insufficient. Cost includes failed/revised attempts; human effort is recorded separately.

**US-11 Resolve quality findings.** As P02, I want issues linked to claims, scenes or assets so that repairs are precise. R1; FR-06, FR-10, FR-20, CR-03, CR-04; J1/J6. Acceptance: Final review exposes findings/disposition. Material factual errors or rights blockers prevent approval, and revised content can be compared with the reviewed version.

**US-12 Approve an exact package.** As P01 acting as reviewer/publisher, I want version-bound approval so that an altered artifact cannot use old sign-off. R1; FR-09, FR-23; J1. Acceptance: Approval binds master/package and permitted scope. Changed master, applicable metadata or destination invalidates affected authority; export/private staging remains distinct from public release.

**US-13 Publish manually.** As P01, I want an export bundle and a channel-result record so that launch does not depend on adapters. R2; FR-23, FR-24; J1. Acceptance: Downloading remains awaiting upload. Actual account, external ID/URL, time and observed status support publication evidence, with verification limits visible.

**US-14 Recover or cancel work.** As P01, I want a clear error and safe recovery so that interruptions do not rebuild everything or repeat public actions. R1; FR-08, FR-28; J6. Acceptance: Compatible completed work/current approvals survive restart. Retries are bounded; cancellation stops further dispatch and uncertain external writes require reconciliation.

**US-15 Connect eligible capabilities.** As P01, I want account identity and permissions shown so that I know what the system can access. R3; FR-11, FR-12, FR-29; J1/J2. Acceptance: Connection records authorized identity/tested capabilities. Ineligible accounts, missing scopes and revocation are explicit; analytics permission never independently enables publishing.

**US-16 Compare opportunities.** As P01, I want editable scores, evidence and effort so that idea selection is inspectable. R3; FR-13, CR-05; J2. Acceptance: Candidates show ratings, rationale, uncertainty and expected cost. Selection persists a contract; high scores cannot bypass rights/factual blockers or be presented as viral probabilities.

**US-17 Release through an adapter.** As P01 acting as publisher, I want explicit transfer/release authority so that the correct video reaches the correct channel. R3; FR-09, FR-15, FR-25; J1. Acceptance: Private staging is explicit where supported and public release uses the approved package. Lost acknowledgements are reconciled before another write.

**US-18 Schedule or cancel release.** As P01 acting as publisher, I want timezone-aware scheduling so that publication follows my instruction. R3; FR-26; J1. Acceptance: Local time is visible and past schedules are rejected. Changed time/package requires applicable approval; external cancellation stays pending until confirmed or explicitly unknown.

**US-19 Verify publication.** As P01, I want the actual link, account, visibility and verification result so that submission is not mistaken for success. R2 manually/R3 connected; FR-24, FR-27; J1. Acceptance: Submitted, scheduled, public and verified outcomes are distinguished. Unavailable playback checks produce PARTIAL with a reason; uncertainty is never invented success.

**US-20 Learn from an experiment.** As P01 acting as analyst, I want supported metrics compared with the recorded hypothesis so that I can choose a defensible next test. R3; FR-11–14, CR-06–09; J4. Acceptance: Results show window, definitions, denominator and baseline/cold-start status. Missing values are not zero; recommendations cite observations, confounders and uncertainty and remain proposals.

**US-21 Produce a varied series.** As P01, later P03/P04, I want shared identity with distinct explanations so that videos remain recognizable and original. R2 internally/R4 customer brands; FR-01, FR-10, CR-01, CR-04, CR-10; J3. Acceptance: Twelve internal originals cover the four series. Repetition is flagged; each episode keeps separate package/release authority.

**US-22 Separate team/client access.** As P04, I want scoped workspaces and assigned roles so that members cannot access or publish another client's content. R4; FR-16, FR-29, CR-10; J7. Acceptance: Membership enforces record/artifact/job/export boundaries. Reviewer access does not imply publishing/billing authority; unauthorized cross-workspace actions are denied.

**US-23 Understand paid usage.** As P03/P04, I want plan limits and consumption visible so that recurring production has known terms. R4; FR-16, FR-17; J7. Acceptance: Applicable subscription/quota terms are visible before activation/use. Exhaustion pauses or follows an explicitly authorized upgrade; recurring proposals never bypass review, spend or release controls.

**US-24 Maintain an explanation.** As P05, I want source changes mapped to scenes so that outdated material can be corrected with history intact. R4 pilot using R1 revision controls; FR-03, FR-04, FR-07, FR-10, FR-20; J8. Acceptance: An approved supplied source revision creates a new version and identifies affected visuals/narration. Published versions remain recorded; replacement releases need applicable approval.

**US-25 Measure a business goal.** As P06, I want a bounded experiment linked to permitted first-party outcomes so that I can assess utility beyond attention. R5; FR-18; J5. Acceptance: Goal, budget, authorized data, outcome definition and window persist before action. Engagement, tracked outcomes and unattributed activity are separated; other campaigns/actions have separate authority.

**US-26 Retain control of data and accounts.** As P01, later P03/P04, I want exports and revocable access so that I control my work and connections. R1 baseline/R3 revocation/R4 customer flows; FR-10, FR-16, FR-29; J6/J7. Acceptance: Export includes permitted records/artifacts; revoked credentials cannot be reused. Deletion follows recorded retention/authority rules across supported stores/caches without claiming removal of external public posts.

### 6.2 Journey map

| Journey | Personas | Trigger and outcome | Release |
|---|---|---|---|
| J1 Idea to channel video | P01/P02, later P03 | Idea becomes an approved, verified original publication | R1 export, R2 manual, R3 connected |
| J2 Evidence to content choice | P01, later P03 | Available evidence becomes a selected opportunity contract | R3 |
| J3 Branded series | P01, later P03/P04 | Series brief becomes distinct approved episodes | R2 internal, R4 customer |
| J4 Performance to next experiment | P01, later P03/P04 | Observation window closes and a qualified next test is proposed | R3 |
| J5 Business goal to outcome | P06 | Goal becomes a permissioned commercial experiment | R5 |
| J6 Revision and recovery | P01/P02 | Change/error becomes a repaired version with history intact | R1; channel branches R2/R3 |
| J7 Customer onboarding | P03/P04 | Pilot receives a scoped usable workspace with known limits | R4 |
| J8 Technical education maintenance | P05/P02 | Approved knowledge becomes an accurate maintainable explanation | R4 using core production |

### 6.3 J1 Idea to approved channel video

**Entry and trigger:** P01 has a project, brand/voice, budget and a worthwhile idea. Connected actions additionally need account authority. **Sequence:** Submit the question; inspect feasibility/evidence; approve narration and storyboard; audition voice; preview; request changes; review the master/metadata; approve the package; select manual/connected distribution; authorize release; inspect actual public results. P02 contributes specialist review. Gates A–E apply.

**Branches:** Missing evidence returns to research; unsupported animation returns to planning before costly work; render errors follow J6. Manual export waits for actual channel evidence. Adapters use private staging where supported and reconcile uncertain writes. **Completion:** The approved output links to its actual account/video, observed public state and verification result; R1 export remains an intermediate result. Stories US-01–13, US-15, US-17–19 apply. Screens: Projects, Evidence, Storyboard, Preview, Package and Publication. Sections 7–10 give the production detail/example.

### 6.4 J2 Audience evidence to content choice

**Entry and trigger:** P01 connects an owned eligible channel or explicitly starts in cold-start mode. **Sequence:** Confirm identity/capabilities; import supported history; inspect availability; receive three to five original hypotheses; compare evidence, ratings, effort and visual payoff; edit priorities; select one; persist its contract/measurement plan; continue to J1.

**Branches:** Sparse data yields exploratory proposals and baseline building. Missing permissions disable the affected capability visibly. Scores cannot bypass evidence/rights blockers. **Completion:** Selection has recorded rationale and a prospective test rather than an unsupported viral prediction. Stories US-02/15/16/20 apply. Screens: Connections, Opportunities and Brief. Section 17 specifies scoring and metrics.

### 6.5 J3 Branded series production

**Entry and trigger:** P01 has a recurring viewer promise and pinned house style. **Sequence:** Select distinct topics/examples; map each to supported animation and its own payoff; pin shared brand/voice; review the slate for repetition; produce through J1; preserve separate episode costs, approvals and releases.

**Branches:** Near-duplicate narratives return to planning. A shared-brand change shows draft impacts without rewriting approved/published versions. Unsupported episodes are honestly simplified, deferred or separately estimated. **Completion:** The internal twelve-video 4/4/2/2 slate has coherent identity and distinct substance. Stories US-01/05/09/21 apply. Screens: Projects/Series, Library, Storyboard and Publication. Customer brand variants remain R4; series selection is not blanket bulk-release authority.

### 6.6 J4 Performance to next experiment

**Entry and trigger:** A publication has a recorded hypothesis/metric and its observation window has elapsed. **Sequence:** Collect snapshots; display definitions/windows; compare compatible content or state cold-start limits; inspect outliers/confounders; record a qualified interpretation; propose another test; let the operator accept/reject it.

**Branches:** Late data remains pending and missing data is not zero. One breakout does not establish a preference; weak reach may still produce an editorial lesson. **Completion:** Evidence links to an interpretable next proposal without automatically authorizing spend/publication. Stories US-16/20 apply. Screens: Analytics, Experiments and Opportunities. The growth study still depends on Section 18's gate.

### 6.7 J5 Business objective to measured outcome

**Entry and trigger:** P06 is in the chosen R5 vertical and provides a specific goal, approved facts, budget and permitted data. **Sequence:** Define a qualified outcome; approve the commercial contract; produce through J1; separately authorize campaign/other actions; inspect first-party outcomes, attribution limits and cost; choose whether to repeat.

**Branches:** Missing conversion access means the business result is unmeasured, not replaced by views. Unsupported/unapproved actions stay blocked. **Completion:** Reporting distinguishes tracked outcomes, unattributed activity and engagement without guarantees. Story US-25 applies. Screens: Future business brief, approvals and outcome report. This adds no launch integration scope.

### 6.8 J6 Targeted revision and failure recovery

**Entry and trigger:** P01/P02 requests a change, finds a factual/visual issue or encounters failure. **Sequence:** Select the claim/scene/run; inspect version/error; request a precise repair or bounded retry; review dependencies, cost and reopened approvals; regenerate affected work; compare; repeat checks; approve the new package.

**Branches:** Budget exhaustion pauses before dispatch; claim changes reopen evidence review; duration changes propagate caption/assembly timing. Reconcile unknown public writes before retrying. Confirm external unscheduling before conflicting replacement release. Published corrections create a proposed repair plan, not silent deletion. **Completion:** Corrected versions/history survive and no stale authority is reused. Stories US-03/07/09–12/14/18/19/26 apply. Screens: Scene editor, Revision impact, Runs and Publication.

### 6.9 J7 Customer and team onboarding

**Entry and trigger:** P03/P04 starts an authorized R4 pilot and reviews actual plan terms. **Sequence:** Create the scoped workspace; complete applicable plan authorization; configure brand/rights; assign member responsibilities; connect required channels; inspect capabilities/usage; finish a sample through J1; verify access and export/revocation controls.

**Branches:** Unavailable integration retains visible export/manual routes. Reviewers cannot publish without authority; users cannot access another client's content. Quota exhaustion pauses or uses an explicitly authorized plan action. **Completion:** The customer can produce a reviewed sample with known limits and enforced boundaries. Stories US-01/12/15/22/23/26 apply. Screens: Onboarding, Workspace, Members, Usage, Connections and Studio. Extra agency administration needs separate planning.

### 6.10 J8 Maintained technical explanation

**Entry and trigger:** P05 supplies approved knowledge or a reviewed derivation and a learner question. **Sequence:** Establish claims/models; simplify with P02 review; map to objects/actions; produce through J1; gather suitable comprehension feedback; when supplied knowledge changes, create a new source/claim version, identify affected scenes and follow J6; approve any replacement release separately.

**Branches:** Misleading simplification returns to review even when rendering succeeds. Unsupported geometry/simulation requires honest deferral or reviewed capability work. Automatic enterprise knowledge synchronization is excluded. **Completion:** Sources/versions are inspectable and later corrections preserve earlier publication history. Stories US-03–06/09/11/24 apply. Screens: Evidence, Storyboard, Revision impact and Publication history.

### 6.11 Story validation and scope control

Validate P01/P02 and J1/J6 through prototype walkthroughs before customer onboarding work. Each delivery card records applicable story IDs and FR/CR coverage and demonstrates observable acceptance with a reviewer. Stories do not independently add integration/release commitments: R4/R5 journeys remain conditional and follow the same authority rules. Acceptance failures create explicit repair work rather than being relabeled completed journeys.

## 7 Complete production lifecycle

### 7.1 Channel setup

The operator creates the project, selects a versioned brand and licensed voice, sets review and budget rules, and chooses the destination channel. For connected distribution, the application displays the actual authorized account identity and tested capabilities. Analytics authorization does not imply publication authority. The reference channel is never treated as the destination.

Store channel/account ID, connection state, scopes, capability checks, timezone, export profile and disclosure settings. Display times in the operator's selected timezone, initially Asia/Kolkata, and store absolute timestamps consistently. The operator determines audience and child-directed settings from applicable content and platform requirements rather than an automatic assumption that educational content is for children.

### 7.2 Production stages

| Stage | Operator experience | Required output |
|---|---|---|
| 1 Capture idea | Enter a topic or select a proposal | Opportunity draft with audience, viewer question and intended payoff |
| 2 Choose brief | Review scope, feasibility, budget and destination | Accepted brief, source plan and proposed measurement window |
| 3 Establish explanation | Inspect sources, assumptions and calculations | Reviewed claim ledger and verified demonstration model |
| 4 Approve script | Read and edit the hook, explanation and conclusion | Approved narration/beat version with claim references |
| 5 Approve storyboard | Review scene compositions, objects and movements | Approved storyboard and supported action plan |
| 6 Compile production inputs | See unsupported operations or rights/layout issues | Validated typed spec, pinned inputs and reserved budget |
| 7 Create voice and timing | Audition pronunciation and pacing | Scene audio, measured alignment, timing and caption segments |
| 8 Render draft | Watch an inexpensive preview | Draft video tied to exact production inputs and actual cost |
| 9 Review and revise | Request targeted changes and inspect their impact | New revision with affected dependencies regenerated |
| 10 Render master | Review final-resolution quality | Immutable master, final captions and production manifest |
| 11 Approve package | Review video, metadata, cover, rights and destination | Versioned approved package and permitted upload scope |
| 12 Upload or hand off | Start authorized private upload or download the bundle | External ID/session mapping, or explicit awaiting-manual-upload state |
| 13 Check readiness | Resolve processing, restriction or metadata issues | Recorded readiness checks and visible unavailable checks |
| 14 Authorize release | Choose the exact account and publish-now or schedule instruction | Current approval and acknowledged release/schedule request |
| 15 Verify publication | See actual link, channel, visibility and verification result | Observed publication record with evidence and remaining limits |
| 16 Learn | Review production costs and later audience observations | Metric snapshots and evidence-linked next experiment proposal |

The system must surface missing essential information without making the operator complete unnecessary setup for every video. Script, storyboard, render and final package remain inspectable independently. A normal action is complete only when its persisted outcome is known; a tool call or upload submission alone is insufficient.

## 8 Approval and publication governance

### 8.1 Human review gates

| Gate | Decision | Approval evidence |
|---|---|---|
| A Brief | Is the idea worth producing with current capabilities and budget | Viewer question, promise, feasibility and cost allowance |
| B Explanation and script | Are claims, demonstration and narration correct and clear | Sources, reviewed derivation/calculations, limitations and script version |
| C Storyboard | Do the visuals explain the idea accurately | Object/action plan, continuity, compositions and narration mapping |
| D Final package | Is this exact master and metadata ready for export or authorized private upload | Final preview, QA, rights, package version and destination |
| E Public release | May this package go public on this account at this time | Current package, account identity, readiness and now/schedule instruction |

These are logical responsibilities, not five compulsory popups. Related reviews may share a screen, but scope and evidence must remain explicit. Agents cannot approve their own editorial or public-release proposals. New claims, material visual changes, changed masters, metadata, accounts or schedules reopen the affected reviews.

Approvals bind actor, immutable version/hash, action scope, destination where applicable and timestamp. Edits create a new version and never mutate an approved master. Earlier approved/published artifacts remain in history. Execution resumes only under still-current approval. Cancellation stops further application actions; external schedules must also be removed and confirmed where applicable.

### 8.2 State and verification

Production states are DRAFT, RESEARCHING, SCRIPT_REVIEW, STORYBOARD_REVIEW, PRODUCING, QA, FINAL_REVIEW and APPROVED_EXPORT, with BLOCKED, FAILED, REVISION_REQUIRED and CANCELLED outcomes.

Publication is tracked separately per platform/account:

| State | Meaning | Next permitted action |
|---|---|---|
| PACKAGE_APPROVED | Exact export package accepted | Authorized private transfer or manual handoff |
| UPLOAD_REQUESTED or UPLOADING | Transfer requested/in progress | Resume or reconcile the recorded session |
| UPLOADED_PRIVATE | External ID and private status observed | Processing and readiness checks |
| READY_TO_RELEASE | Required available checks passed | Obtain applicable public-release decision |
| RELEASE_REQUESTED | Approved publish/schedule write submitted | Reconcile external response |
| SCHEDULED | Future release acknowledged | Monitor release or confirm external cancellation |
| PUBLISHED | Public status observed on intended account | Verify presentation and collect available metrics |
| PUBLICATION_UNKNOWN | External outcome not established | Reconcile or request operator verification before retry |
| BLOCKED or FAILED | Known issue prevents progress | Explain, repair and reopen approvals as needed |
| CANCELLED | Further actions stopped and external cancellation confirmed where relevant | Retain history; require current authority for new requests |

Store provider processing status independently, including last-checked time. Verification is NOT_CHECKED, PASSED, PARTIAL or FAILED. A public API flag does not prove playback for every viewer context. A manual export remains awaiting upload until actual external evidence is recorded. Existing released content is not automatically deleted or replaced after a factual correction is discovered.

## 9 Signal Motion Engine

### 9.1 Library boundaries

Own the visual grammar, typed scene specification, original components, brand tokens and revision rules. Reuse established renderers. The compiler accepts bounded data and maps it to reviewed application code; it must never execute arbitrary LLM-generated JavaScript, Python or source-page instructions.

| Initial family | Required behavior | Representative use |
|---|---|---|
| MathExpression | Addressable terms, fractions, operators, powers and equations | Highlight a term and connect it to visible objects |
| NumberSequence | Identifiable terms with stable meaning and color | Build odd-number sequences or verified digit patterns |
| GeometricArrangement | Bounded grid, ring, line and group layouts | Grow a square or place digits around a circle |
| ObjectTransform | Move, rotate, scale, regroup and explicitly map transformations | Place an L-layer or rearrange a sequence |
| FocusHighlight | Reveal, outline, emphasize and dim | Direct attention to the active explanatory element |
| CaptionAndTakeaway | Phrase captions, question text and concise conclusions | Synchronize narration and the final insight |

These six composable families replace the earlier generic first-spike list. They do not eliminate the longer-term semantic library. Add ConceptReveal, ConceptCompare, ProcessFlow, LoopAndRetry, StateTransition, Timeline, BeforeAfter, BarComparison, TrendLine, NetworkGraph, CauseEffect, StepByStep, MythVsReality, DataCallout and ClosingTakeaway as selected briefs justify them. The previous 12–15 component target is an expansion direction, not a prerequisite to proving one video.

What-if stories need reviewed parameters and clear assumptions; everyday mechanisms may need layers, zoom and object relationships; puzzles need deterministic solution states; technology explanations need messages, loops and networks. The capability check must reject or expose a missing visual operation before expensive production.

### 9.2 Objects and timing

Stable object IDs preserve semantic identity, color and grouping across movement. Value transformations explicitly map old and new terms. A verified demonstration model provides counts, units, coordinates or relationships through reviewed allowlisted functions. Exact arithmetic or documented numerical tolerance must agree with displayed values. Illustrations and approximations are labeled.

The action timeline contains supported operations, target IDs, frame intervals, bounded parameters, easing tokens and event/phrase anchors. Unsupported actions, excessive objects, invalid references, out-of-bounds timing and unlicensed assets fail validation. Pin one frame rate; the proposed reference is 30 fps. Measured narration duration, not an LLM estimate, determines feasible final timing.

Persist scene entry/exit state and continuity dependencies. Prefer self-contained scene inputs that reconstruct required state, while checking continuity at cuts. A preceding change can invalidate a following scene when it changes inherited state. Captions and equations must remain readable at phone size and outside platform obstruction zones.

### 9.3 Rendering and selective revision

Hash canonical scene parameters, calculation outputs, assets, brand/fonts, voice settings, component/renderer versions, relevant timing and entry state. Reuse local scene clips only when effective dependencies match. A text change may require TTS, alignment, captions, video, adjacent transitions and final mix. Duration changes shift assembly and caption offsets. Brand or narrator changes may invalidate many scenes.

Design transition handles explicitly. Reassemble a new master when effective inputs change even if most scene clips are reused. Before regeneration, show what will be rebuilt, estimated cost and affected approvals. Preserve earlier masters. Pin fonts, seeds and encoding configuration; target reproducibility within documented encoding tolerance rather than identical MP4 bytes across every environment.

## 10 Original reference storyboard

### 10.1 Brief and demonstration

Proposed first prototype: **Why do odd numbers build a square?** A curious beginner sees how consecutive odd-number layers form larger squares. Use an original dark theme, accessible colored layers, one narrator and timed subtitles. The sample belongs to mathematical visual discovery and can be tagged Solve This when the experiment is created.

For positive integers n, adding the first n odd positive integers gives n squared. Growing the square from side k minus one to side k adds 2k minus one unit cells. Verify every count and coordinate through reviewed integer arithmetic; the first five examples are 1, 4, 9, 16 and 25 cumulative blocks. Demonstrate the general construction rather than claiming five observed values alone prove the rule.

### 10.2 Proposed 45 second sequence

The target is 1,350 frames at 30 fps. Recompile timing after measured narration and review any material pacing change.

| Beat and target time | Visual demonstration | Narration intent |
|---|---|---|
| Hook 0–4 seconds | Reveal 1 + 3 + 5 + 7 + 9 = 25 beside a faint square outline | Ask why adding odd numbers makes a square |
| Setup 4–10 seconds | Place one block, then a three-block L to form a two-by-two square | Establish one, then four blocks |
| Demonstration 10–22 seconds | Add five, then seven blocks; update totals as each layer settles | Connect each new odd number to a larger square |
| Explanation 22–33 seconds | Add nine blocks; highlight a five-cell edge and four-cell edge without counting the corner twice | Explain a row plus a column with their corner shared |
| Payoff 33–41 seconds | Connect colored terms to layers and show the general relationship | Explain why the first n odd numbers fill an n-by-n square |
| Closure 41–45 seconds | Hold the completed square, short takeaway and discreet brand cue | Leave the viewer with the geometric insight |

Blocks have stable coordinate-based IDs. Each L-layer retains its semantic color; equation terms link to those groups. The final layer has nine new cells, not ten. Captions must not cover active layers, dimension labels or equations. Include a reviewed derivation or mathematical reference in the actual claim ledger before publishing.

### 10.3 Revision and publication example

If the operator says “hold the row-and-column explanation two seconds longer and make the corner clearer,” show the affected scene, highlights, narration/captions and downstream timing. Offer a 47-second total or a shorter other beat. Regenerate affected dependencies, reassemble, recheck and obtain applicable package review. Do not claim later offsets stay unchanged.

The proposed title is “Why Odd Numbers Build Perfect Squares.” The package includes master, captions, original cover, description with reviewed attribution, rights, versions and cost. Upload privately on the authorized YouTube channel where connected; check readiness; obtain the exact public-release instruction; verify its actual URL, account and observed public status. A manual upload follows the same review responsibilities and is explicitly recorded as manual.

Record the hypothesis before publication: a constructive geometric explanation makes the pattern understandable to beginners. Choose an available primary audience metric and a seven-day window as an initial proposal. Retention is an attention signal, not proof of comprehension; include editorial/user feedback where available. This storyboard is a planning example, not an approved or published video.

## 11 Functional requirements

Existing FR identifiers are retained. FR-19 onward formalize the visual-storytelling and complete-publication requirements. Acceptance is assessed at the applicable release in Section 4, not inferred from a demo.

| ID | Priority | Required capability | Acceptance evidence |
|---|---|---|---|
| FR-01 | P0 | Brand kits and scoped projects | Project/settings isolated; brand version pinned per render |
| FR-02 | P0 | Topic intake and opportunity brief | Audience, viewer question, promise, format, evidence and budget persist |
| FR-03 | P0 | Research and source management | Every material factual claim has supporting evidence or remains blocked pending review |
| FR-04 | P0 | Outline, script and storyboard | Each layer can be inspected, revised and approved independently |
| FR-05 | P0 | Typed versioned scene specification | Invalid scenes/actions/references fail with actionable errors |
| FR-06 | P0 | Branded video, narration and captions | Selected dimensions, measured timing and no known clipping/overflow |
| FR-07 | P0 | Targeted revision and reuse | Compatible artifacts reused; changed timing/state dependencies honestly invalidated |
| FR-08 | P0 | Run, attempt, retry and cost records | Operator can inspect state, failures, spend and recovery actions |
| FR-09 | P0 | Version-bound approval | Stale approvals rejected; public action requires account/action/version authority |
| FR-10 | P0 | Provenance and rights | Source, license, prompt/spec/model/tool version and approval records linked per output |
| FR-11 | P1 | YouTube analytics | Supported authorized metrics imported; missing/late values labeled |
| FR-12 | P1 | Instagram connection | Only verified eligible capabilities enabled; limitations visible |
| FR-13 | P1 | Evidence-linked opportunity ranking | Rationale, baseline, sample size, uncertainty, effort and experiment goal visible |
| FR-14 | P1 | Experiment tracking | Hypothesis, treatments, baseline, windows, confounders and observations persist |
| FR-15 | P1 | Connected publishing and recovery | Authorized transfer/release; reconciliation prevents blind duplicate writes |
| FR-16 | P2 | Customer workspaces and roles | Tenant isolation, onboarding, quotas and billing verified before paid beta |
| FR-17 | P2 | Recurring proposals | Scheduled suggestions respect current review/budget/publication rules |
| FR-18 | P3 | Business conversion objectives | Permissioned first-party outcomes separated from engagement and unattributed action |
| FR-19 | P0 | Persistent visual objects | Stable identity/meaning/color and explicit transformation mapping demonstrated |
| FR-20 | P0 | Verified demonstrations | Displayed counts, equations, units and geometry match reviewed calculations/models |
| FR-21 | P0 | Narration and action alignment | Measured phrase/event timing; understandable pacing and pronunciation |
| FR-22 | P0 | Capability and cost preflight | Unsupported operations/rights and budget gaps exposed before paid dispatch |
| FR-23 | P0 | Complete publication bundle | Approved master, captions, script, metadata, cover, attribution, rights and costs available |
| FR-24 | P0 | Manual publication evidence | Export never counted as publication; actual destination, URL, time and verification recorded |
| FR-25 | P1 | Private transfer and readiness where supported | Explicit privacy, external ID and available processing/readiness evidence stored |
| FR-26 | P1 | Scheduling and cancellation | Future time/timezone validated; changed instructions reapproved; external cancellation confirmed |
| FR-27 | P1 | Publication verification | Intended account/public status checked; presentation checks and limits reported |
| FR-28 | P0 | Recovery and cancellation | Bounded retries, timeout, resume, manual takeover and stop behavior demonstrated |
| FR-29 | P0 | Baseline security and retention | Authentication, ownership, protected credentials, private artifacts and retention rules enforced |
| FR-30 | P0 | Production measurement | Human effort, quality, revisions and total cost recorded per approved video |

FR-24 supports R2 manual distribution; FR-25–27 complete connected behavior in R3. Final-package review, source rights and public-release authority remain mandatory in both routes. Where a platform lacks private staging, approval must precede the first operation that could publish.

## 12 Content and experiment requirements

| ID | Priority | Required behavior | Acceptance evidence |
|---|---|---|---|
| CR-01 | P0 | Four distinct editorial series | Twelve approved original public videos across the 4/4/2/2 slate at R2 |
| CR-02 | P0 | Editable opening and hook | Opening can be previewed/revised with compatible unrelated scenes reused |
| CR-03 | P0 | Accurate visual explanation | Reviewed claims, calculations and representative visuals agree |
| CR-04 | P0 | Brand consistency with narrative variety | Full-slate review flags near-identical stories, wording and scene patterns |
| CR-05 | P1 | Editable Content Opportunity Lab | Component ratings, rationale, evidence, effort, cost and contract persist |
| CR-06 | P1 | Platform-aware metrics | Every measure has source, definition, window, denominator or availability flag |
| CR-07 | P1 | Diagnostic recommendations | Each recommendation cites observations, alternatives and uncertainty |
| CR-08 | P1 | Conditional growth experiment | Twelve-video gate precedes experiment; planned/actual originals and uploads distinguished |
| CR-09 | P1 | Reach and audience outcomes separated | Cross-platform views never presented as deduplicated people |
| CR-10 | P2 | Customer brand/series variants | Workspace ownership, brand separation and cost limits verified |

## 13 Studio experience

The initial Studio supports project intake, source/script review, storyboard/preview, final package/export and run recovery. Chat can create or revise drafts, but structured controls remain available for inspecting state and consequential actions. Defer professional multi-track editing and a universal timeline editor.

| Surface | Required operator controls | Release |
|---|---|---|
| Projects and briefs | Topic, series, audience, budget, brand version and destination | R1 |
| Script and evidence | Side-by-side claims, sources and narration; edit/approve/return for revision | R1 |
| Storyboard and preview | Scene cards, playhead, object/action properties, timing and citations | R1 |
| Revision impact | Affected dependencies, expected reuse, cost and reopened approvals | R1 |
| Package and export | Master playback, QA findings, rights, metadata, captions and approval | R1 |
| Runs and recovery | Task attempts, costs, errors, retry/cancel/resume and reason | R1 |
| Publication record | Manual handoff and actual channel evidence | R2 |
| Opportunities and analytics | Ranking, experiment history, comparable metrics and limitations | R3 |
| Publishing calendar | Account, current package, schedule, status, uncertainty and cancellation | R3 |
| Asset and brand library | Approved reusable objects/assets, licenses and version history | Basic R1; expanded R4 |

Keep errors actionable: identify the scene, object, claim or account and the next repair option. Show estimated and actual spend, progress and blocked states without presenting technical execution details as editorial decisions. Unavailable analytics are visibly unavailable rather than empty successes.

## 14 Agent tasks and workflow architecture

Use a modular application with separately executable media workers. A durable workflow owns execution transitions and approvals; a dependency graph determines permitted concurrent tasks; bounded specialist tasks perform reasoning. An append-oriented evidence and artifact ledger links decisions to inputs and outcomes.

### 14.1 Task responsibilities

| Responsibility | Input and output | Execution boundary |
|---|---|---|
| Creative direction | Objective to accepted brief and narrative plan | Bounded planning; no authority to commit public actions |
| Research | Topic/claims to evidence, contradictions and review flags | Untrusted sources; citations validated and human reviewed |
| Script editing | Accepted explanation to narration and beats | Structured output with claim and version references |
| Storyboarding | Approved script to objects, supported actions and scene specification | Capability-aware; deterministic compiler validates |
| Narration and production | Approved inputs to audio, captions, clips and master | Software workers using licensed providers and reviewed components |
| Quality review | Inputs/output to findings and recommendations | Deterministic checks plus optional model critique and human review |
| Publishing | Approved package/action to external state | Deterministic adapter; least privilege and reconciliation |
| Audience analysis and learning | Available aggregates to hypotheses and comparisons | R3; uncertainty and baseline controls |

Initially implement research, script and storyboard as three bounded model tasks. Narration, rendering, validators and transfer are services, not separate autonomous runtimes. The role catalog does not require ten agents or another graph framework. Each task contract defines input, output schema, permitted tools, budget, retry ceiling, failure states and evaluation fixtures.

### 14.2 Proposed implementation baseline

| Layer | Initial recommendation | Decision constraint |
|---|---|---|
| API and domain logic | Python and FastAPI | Provider-neutral content services and authorization |
| Studio and scene library | TypeScript and Next.js/React | Shared component previews and structured editing |
| Durable execution | Temporal after restart/replay spike | Avoid a custom durable workflow framework |
| Business records | PostgreSQL and migrations | Versioned contracts, scope and queryable execution projections |
| Artifacts | S3-compatible object storage | Immutable private media and manifests |
| Composition and encoding | Remotion and FFmpeg | Verify licensing and benchmark actual sample quality/cost |
| Specialized mathematical rendering | Manim only where justified by a selected brief | Evaluate adapter during spike rather than requiring two renderers |
| Voice and models | Swappable provider adapters | Select using quality, rights, capability, cost and evaluation evidence |
| Delivery and observability | Containers, GitHub Actions, structured events and traces | Reproducible local/staging environment and inspectable operations |

These are recommendations requiring architecture decisions, not product requirements to use a specific vendor. R0 may use a command-line pipeline. Do not add Kubernetes, microservice fleets, foundational model training or a Rust migration as launch dependencies. Python handles content/integrations; TypeScript handles Studio/media composition. A future Rust worker requires evidence of a remaining bottleneck; language substitution alone does not establish faster rendering.

The workflow owns execution progression. PostgreSQL owns content, artifact and approval versions; run-state tables are queryable projections, not an independent competing state machine. Use expected-version commands, idempotent activity writes and a durable request/outbox to reconcile lost workflow-start/signal acknowledgements. External I/O, model calls and media work run outside replayable workflow decision code. Workers cannot advance lifecycle authority independently.

## 15 Data and interface contracts

| Record or contract | Required fields and relationships |
|---|---|
| Workspace and project | Owner/members, permissions, quotas, brand and data scope |
| Channel | Platform/account identity, authorization, capability and consent/revocation state |
| AudienceProfile | Authorized aggregate inputs, segments, sample size and last update |
| Content Opportunity Contract | Audience need, hypothesis, evidence, objective, deliverables, budget, approvals and measurement plan |
| Experiment | Treatments/baseline, primary metric, windows, confounders and observations |
| CreativeBrief and ScriptVersion | Promise, beats, narration, scene/claim IDs and review/version state |
| Claim and EvidenceRecord | Claim/type, source metadata/URL, retrieval time, supporting location/excerpt, contradiction and reviewer status |
| DemonstrationModel | Domain/units, reviewed function/model version, parameters, computed results and tolerance/rounding |
| VideoSpec and SceneVersion | Schema version, brand, supported types, objects/actions, frame timing, layout and claim/asset links |
| Timing and RenderManifest | Audio alignment, frames/transitions, entry/exit state, input hashes, fonts/renderer/codec versions and dependencies |
| Asset | Location, type, hash, origin, rights/license, expiry where applicable and lifecycle |
| ExecutionRun and TaskAttempt | Workflow/task IDs, states, attempts, prompts/models/tools, failures, retries and spend |
| Approval | Actor, immutable target version/hash, action scope, account where relevant and timestamp |
| Publication | Account, package/master/metadata versions, transfer/external IDs, URL, schedule, observed status and verification |
| PerformanceSnapshot | Raw/normalized measure, platform definition/API version, window, denominator, availability and import time |
| LearningRecord | Hypothesis, observation, uncertainty, interpretation and proposed next experiment |

Generate JSON Schema and TypeScript types from a canonical schema source, provisionally Pydantic models, and test shared valid/invalid fixtures in both runtimes. Pin schema versions and migrate deliberately. Avoid independently maintained incompatible definitions. Stable IDs and immutable versions are required even if the chosen schema technology changes.

Keep large media out of the database. Scope records, object references, background jobs and exports to the workspace. Store source excerpts only to the extent permitted. Keep superseded artifacts according to retention rules and retain what is needed to explain a publication. A platform's transcoded playback bytes need not match the submitted master hash; provenance establishes what was submitted and to which external ID.

## 16 Publishing and platform integrations

Connected account capabilities are established by an account-specific preflight, not assumed from general documentation. Verify authorization, quota, allowed media, metadata, publication and analytics routes, credential refresh/revocation, and the exact observation fields available. Never silently substitute browser automation or private-data scraping for a missing API.

For YouTube, explicitly request private visibility for the staging transfer, retain the resumable session/external ID securely, and inspect available processing/readiness information before release. Current API documentation supports status and scheduling fields; implementation must validate the applicable private/unpublished conditions. Reject past schedule times in the application. An omitted privacy value must not be used as a safe default [S1–S4].

For Instagram, verify the eligible professional-account route, scopes, app/access requirements and actual endpoints. If no private staging exists for the verified route, keep the package internal until approval of the first operation capable of publication. Do not invent draft states or assume YouTube's processing workflow applies. Export remains a supported fallback [S8–S9].

Approval of a publication includes destination, current master/metadata package, and publish-now or future-time scope. A changed schedule or package needs applicable approval. After network loss, reconcile the recorded transfer or external state before another write. When uncertain, retain PUBLICATION_UNKNOWN and request verification; no exactly-once guarantee is inferred for external APIs.

Publication completion requires an external record on the intended account, observed public status, required metadata consistent with the approved package, no known blocking processing failure, and visible verification evidence or limits. A partial playback check is reported as PARTIAL. Manual upload records must include actual account, external ID/URL, time and evidence. Scheduling a post is an authorized future release, not final proof that it has become public.

If an approved schedule is cancelled or changed, confirm the platform-side action. Until confirmed, show the existing schedule and block conflicting replacement actions. A post-publication correction is surfaced to the operator; the system does not silently delete or replace released content.

## 17 Audience intelligence and experimentation

### 17.1 Inputs and measurement dictionary

Use permissioned owned-channel aggregates and permitted public editorial research. Do not infer identifiable viewers' preferences. Record raw definitions before normalization. Missing, delayed, unsupported and permission-denied values remain distinct from zero.

| Measure when available | Intended interpretation | Required limitation |
|---|---|---|
| Initial choice or stayed-to-watch | Opening clarity and topic fit | Platform/endpoint availability and definitions differ |
| Average duration or engaged watch time | Active attention | Compare compatible duration groups and denominators |
| Percentage viewed or retention profile | Progress through the explanation | Replays/loops can affect interpretation |
| Completion/replay measures | Payoff or repeated interest hypothesis | Does not independently establish intent or comprehension |
| Shares/saves per eligible reach/views | Useful or remarkable content hypothesis | Use the actual supported denominator |
| Subscriber/follower and returning audience | Interest in future content and series | Requires suitable history; attribution is limited |
| First-party enquiries/bookings later | Potential business contribution | Permissioned tracking and attribution limits |

### 17.2 Content Opportunity Lab

The Lab compares ideas before costly production. It shows title, audience, viewer question, why it matters, sources, uncertainty, proposed animation family/payoff, research/render effort and cost, risks and primary metric. The editor can change ratings and see the rationale. A high score cannot bypass evidence, rights or review blockers.

| Editorial dimension | Initial weight |
|---|---:|
| Broad curiosity | 25 percent |
| Clear visual payoff | 25 percent |
| Storytelling strength | 20 percent |
| Natural sharing potential | 15 percent |
| Originality and factual confidence | 15 percent |

The initial unvalidated score is the sum of each percentage weight multiplied by its one-to-five rating and divided by five. Ratings 4, 5, 4, 3 and 5 produce 85 out of 100. This is a prioritization heuristic, never a probability of virality. Low-evidence ideas remain exploratory. Later calibration can study associations within comparable groups without claiming causation.

### 17.3 Experiment method and diagnosis

Before publication, record the question, falsifiable hypothesis, treatment, primary metric, baseline or explicit cold-start status, measurement window and known constraints. An initial seven-day window with later follow-up is a proposal, not an API guarantee. Compare by platform, topic, format, duration and publication period. Record sample size, seasonal effects, promotion, hook, narration pace and scene density. Reserve exploration capacity and avoid overfitting an outlier.

| Observation | Investigation | Possible next experiment |
|---|---|---|
| Weak opening signals | Unclear first frame, framing or audience mismatch | Change the opening question/visual |
| Strong opening then steep drop | Confusing mechanism, clutter, slow pacing or late payoff | Simplify or restructure the middle |
| Good retention but limited distribution | Topic breadth, fit, sample size and distribution context | Try an adjacent topic |
| High reach but weak return interest | One-off appeal outside the channel promise | Test an original related series |
| Watch time but little sharing/saving | Utility or memorable takeaway may be weak | Add a clearer final explanatory visual |

These are hypotheses, not platform ranking rules. Do not use invented universal viral thresholds. Evaluate recommendations against a simple editorial baseline on repeated useful production or audience observations. Early twelve-video results mainly test production and content quality, not statistically prove audience optimization.

## 18 Conditional growth experiment

The twelve-video quality/cost gate precedes the larger experiment. If it passes and capacity remains acceptable, test up to four original videos per week for twelve weekly slates, or **48 additional originals**, inside a 90-day study. Adapt them for both channels only when eligible and separately approved, creating up to 96 platform uploads. The twelve qualification videos are a preceding validation slate, not silently counted inside those 48.

Twelve weekly slates cover 84 days; the remaining study period supports observation and consolidation. A full seven-day result window for the latest posts can extend beyond day 90 and must be reported as follow-up. Four per week is a capacity ceiling, not a quota that overrides quality.

| Study period | Maximum proposed originals | Learning objective |
|---|---:|---|
| Days 1–30 | Up to 16 | Explore topics, opening forms, pacing and visual complexity |
| Days 31–60 | Up to 16 more | Repeat promising approaches, challenge weak hypotheses and preserve exploration |
| Days 61–90 | Up to 16 more | Refine series and production consistency; consolidate observations |

The stretch milestone is 1,000,000 cumulative platform-reported organic views for experiment uploads during the defined reach window. Across 96 uploads, the arithmetic average would be approximately 10,417 views per upload; actual outcomes can be skewed and much lower. Fewer eligible uploads change the required average. Views on one upload, summed cross-platform views and deduplicated people are different outcomes. Do not claim unique reach from summed views or promise monetization.

Track engaged/qualified attention separately where available. Growth targets never override accurate claims, original value, rights or release authority. A low-reach video may still yield a useful lesson; misleading viral content fails the editorial gate. Paid expansion requires separate customer evidence.

## 19 Quality and release acceptance

### 19.1 Editorial rubric

Assess factual and visual correctness, clarity, original explanatory value, readable motion/audio/captions, and promise/payoff fulfillment. A proposed starting rubric is one to five per dimension with no dimension below four, no unresolved material factual error, and no rights blocker. Calibrate and adopt the threshold during discovery before judging the validation slate. Human review must include the final-quality master, not only the draft.

Verify source adequacy and contradictions, not just URL existence. A calculation can be correct while its visual explanation is misleading. General proofs, examples, approximations and illustrative models must be distinguished. Review the muted/captioned explanation and pronunciation as well as the narrated result. Do not approve generic or misleading work to meet a cadence target.

### 19.2 Verification matrix

| Check | Required evidence | Main requirement coverage |
|---|---|---|
| QA-01 Contracts | Invalid scenes/actions, missing objects/claims/assets and schema drift rejected | FR-03–05, FR-19–20 |
| QA-02 Demonstration | Computed values, cell counts, units, domains and displayed geometry agree | FR-20, CR-03 |
| QA-03 Media | Dimensions, duration, audio, caption bounds, long labels and safe zones checked | FR-06, FR-21 |
| QA-04 Continuity and revision | Stable identities, entry/exit state, transitions, changed timing and global-brand invalidation verified | FR-07, FR-19 |
| QA-05 Authority | Stale approval, changed metadata/account/schedule and cancelled run cannot cause unauthorized release | FR-09, FR-26 |
| QA-06 Recovery | Worker crash, duplicate delivery, provider timeout, exhausted budget and cancellation demonstrated | FR-08, FR-28 |
| QA-07 Publication | Lost upload/release acknowledgement reconciled; unknown state not blindly retried | FR-15, FR-25–27 |
| QA-08 Evidence and rights | Unsupported claims, fabricated references, expired/unlicensed assets and unsafe source instructions flagged | FR-03, FR-10 |
| QA-09 Operator journey | Create, review, render, targeted revise, approve, export and channel-record journey completed | FR-02–09, FR-23–24 |
| QA-10 Isolation | Cross-workspace database/object/job/export access denied; credentials/logging protected | FR-16, FR-29 |
| QA-11 Metrics | Missing values, different definitions/windows and small samples represented honestly | FR-11–14, CR-06–09 |
| QA-12 Operations | Representative backup restored; deletion/revocation path and alerts demonstrated | FR-28–30 |

CI runs fast schema, authorization, workflow and unit checks plus a lightweight render fixture. Maintain representative frame comparisons with tolerance and human motion review. Run expensive full renders and live-provider evaluations on demand or a budgeted schedule. Persist prompt/model/tool versions, inputs, outputs, reviewer judgment and costs. The evaluation corpus includes all four series, conflicting/unsupported sources, long narration/labels, invalid specs, prompt injection, unsafe asset URLs and revision cases.

Story-based acceptance walkthroughs must cover the relevant personas, main path, revision/failure branch and observable outcome in Section 6. QA-09 includes these walkthroughs; QA-05/07/10 verify the associated authority, publishing and role boundaries. Later customer/business journeys are evaluated only at their assigned releases.

### 19.3 Release gates

| Gate | Required acceptance |
|---|---|
| R0 | One accurate original visual story, timed narration/captions, targeted revision, measured cost/render time and object continuity |
| R1 | P0 technical production journey through the UI; no unresolved approval-bypass or access-control defects; visible bounded recovery and provenance |
| R2 | Twelve reviewed originals across four series, actual public records, rights, effort/cost and quality results; compare effort with a documented manual baseline |
| R3 | Working permissioned measurement and feasible publishing routes; explicit unavailable capabilities; one prospective experiment with comparable baseline or cold-start status and documented results |
| R4 | At least three paid pilots with repeat use; enforced tenant controls, onboarding, quotas/billing, deletion/export and measured margin/support burden |
| R5 | One narrow vertical with permissioned conversion signals and evidence of utility beyond engagement |

Before R2, adopt an explicit production reliability threshold. The planning proposal is at least 10 of 12 completed without code-level repair; report the exact actual rate and all manual work. All twelve still need acceptable editorial quality. Failure to meet the adopted threshold triggers repair/re-estimation, not retroactive redefinition. Recommendations must demonstrate repeated usefulness against a simple editorial baseline before broader audience-optimization claims.

## 20 Nonfunctional requirements and operations

| Dimension | Requirement | Validation approach |
|---|---|---|
| Reliability | Durable execution, idempotent internal writes, bounded retries/timeouts and honest external uncertainty | Restart, duplicate-delivery and unknown-outcome scenarios |
| Performance | Prioritize useful draft previews; measure final rendering rather than promising untested speed | First-sample baseline and representative workload measurements |
| Reproducibility | Pin effective inputs, font/render/tool versions and seeds within documented tolerance | Repeated fixture outputs and explainable differences |
| Security | Authentication, workspace authorization, least privilege and private artifact access | Ownership/access tests, credential and signed-access review |
| Cost control | Reserve budgets before concurrent dispatch, reconcile actual use and stop when insufficient | Cap, retry and cancellation cases |
| Accessibility | Accurate captions, contrast, legible notation, safe zones and non-flashing motion | Phone-size, muted and motion review |
| Observability | Trace run/task/attempt/content/artifact IDs, costs and failures | Operator can explain an output and recover a failed step |
| Data governance | Retention, export, deletion, access audit and revocable connections | Documented and tested lifecycle, including cached copies |
| Portability | Versioned content/scene contracts independent of one provider | Adapter fixtures and exportable artifacts |
| Resource isolation | Bounded render CPU/memory/time and object/asset sizes | Limit tests; no arbitrary generated-code execution |
| Deployability | Reproducible local/staging setup, separate credentials, reviewed migrations and rollback | Deployment/rollback and compatibility checks |
| Continuity of service | Database/artifact backups and representative restoration | Restore content, manifest and run references |

Treat source pages, model outputs and assets as untrusted. Prevent private-network/metadata-service fetches, bound downloads and validate file types. Encrypt/restrict platform credentials, redact secrets and transfer-session URLs from logs, and enforce ownership through jobs, object access, exports and support tooling. Before paid beta, test every tenant boundary; adding a tenant ID alone is insufficient.

Monitor stuck runs, queue delay, render duration and memory, provider errors, retry spend, failed approvals, publication uncertainty and cost per approved output. Operators need cancel, bounded retry, resume, reconcile, revoke account and export-evidence controls. Distinguish retryable provider failure, invalid content, deterministic render defects and uncertain public actions; each requires different recovery.

## 21 Costs and commercialization

### 21.1 Production economics

Choose a monthly ceiling and per-video allowance before scaling provider calls. Monetary limits are open decisions; no sustainable amount can be inferred before the sample is measured. Record currency and exchange-rate assumptions where needed.

Variable cost per approved output includes all research/model calls, TTS, generated media, render compute, allocated storage/egress, revisions and failed attempts. Report fixed infrastructure and applicable licensing separately and allocate them for unit economics. Record active human minutes independently and include their cost when assessing a service. The denominator is approved outputs, not just successful render attempts.

Use vector/diagram animation by default. Generative illustrations are optional and budget-capped; extensive generative video is deferred. Reserve estimated task costs before parallel dispatch, reconcile actual spend afterward and prevent unbounded repair loops. Budget approval permits bounded execution within scope; it is not recurring authority for arbitrary new spend.

### 21.2 Commercial validation

Test a creator/studio subscription with bounded render/generation usage and optional additional credits. Earlier illustrative monthly ranges, US$29–79 for creators and US$99–249 for studios, remain willingness-to-pay hypotheses, not adopted prices or margin evidence. Validate heavy-user behavior, licenses, payment costs, support and onboarding before deciding a price.

Interview established creators/studios with recurring production budgets and inspect their recent workflow. Compare a real manual baseline against quality, time, revisions and cost in OpportunityOS. Seek a narrowly scoped paid pilot before adding agency administration. A secondary commercialization path is licensing the semantic library/API to education or technical-content teams if that demand proves stronger.

Measure paid conversion, weekly active production workspaces, approved videos, hours avoided, contribution margin, acquisition cost where measurable, support workload and 30/60/90-day retention with cancellation reasons. Retention should come from reliable recurring value, reusable context and measurable improvement, with transparent exports rather than data lock-in.

## 22 Roadmap and effort assumptions

Discovery establishes twelve briefs, the quality rubric, original motion/voice references, competitor/manual workflow baseline and provider/access feasibility. Prove one mathematical visual story before broad library or dashboard work. Expand into the full series slate, complete the internal operator experience, and validate the channel. Invest in customer and business capabilities only after their gates.

### 22.1 Internal engineering milestones

| Milestone | Main deliverable | Indicative engineering hours |
|---|---|---:|
| M0 Discovery | Twelve briefs, first three selected, style/rubric, budget, rights and access preflight | 16–24 |
| M1 Animation feasibility | Six families, verified demonstration, object continuity, TTS/captions and revision spike | 32–48 |
| M2 Control plane | Repository/CI, authentication, records/object store, durable execution, approval and cost foundation | 40–64 |
| M3 Content tasks | Research, claim review, script, storyboard/action planning and evaluation fixtures | 36–60 |
| M4 Internal Studio | Evidence/script review, storyboard, preview/edit, impact, package/export and runs | 56–88 |
| M5 Channel usability | Manual records/bundles, platform probe and one small feasible adapter only if estimated | 24–40 |
| M6 Stabilization | Regression fixes, resource limits, backup/restore, operating documentation and baselines | 24–40 |
| Total | Narrow internal release and limited distribution capability | **228–364** |

These are unmeasured allowances for an experienced engineer using AI assistance, not commitments. They assume narrow UI/component scope and exclude external-review waiting, full customer SaaS and unestimated publishing work. Re-estimate after M1, especially mathematical typography, animation polish, audio and revision complexity. The complete R3 scheduling/reconciliation suite requires a separate estimate; it is not silently included in M5.

Reserve another provisional **60–120 operator/content hours** for the twelve-video validation and additional capability needs. Avoid double-counting engineering/content overlap. Large new animation families require explicit re-estimation. The combined allowance is **288–484 hours**, excluding a separate contingency reserve.

| Sustainable capacity | Approximate calendar equivalent |
|---|---|
| 20 hours per week | 15–25 weeks |
| 25 hours per week | 12–20 weeks |
| 40 hours per week | 8–13 weeks |

Availability is not confirmed. Coding assistance does not eliminate factual review, integration debugging or animation evaluation. From 12 November 2026, roughly seven weeks remain until early January 2027, or about 140–175 hours at 20–25 hours per week. If January remains the channel target, launch a smaller production/review tool with three to five strong originals, manual uploads and manual analytics, then continue toward the full Studio and twelve-video gate. That smaller launch does not authorize the 48-video study.

### 22.2 First work cycle

Week one freezes the slice, selects three representative topics from the twelve-brief slate with one mathematical story first, establishes original motion/voice references, checks rights/access and defines typed objects/actions and verified calculations. Week two starts the renderer, narration, captions and targeted revision, recording actual cost, resource use and human minutes. At part-time capacity, the full six-family spike may extend into week three.

After the sample, improve storytelling or animation before expanding orchestration if those are the weak points. Reconsider the renderer before coupling the Studio to it if it cannot meet the output standard. Calendar commitments follow the measured spike.

## 23 Workstreams and ownership

These are responsibilities rather than required headcount. One implementer may own several, but every card has an accountable owner and review evidence. Specialist editorial review is assigned where needed.

| Workstream | Main responsibility | Suggested accountable role |
|---|---|---|
| Product and scope | Release boundaries, decisions, acceptance and prioritized cards | Product owner/operator |
| Editorial and research | Briefs, source review, narration and originality | Editor/fact reviewer |
| Brand and motion | Motion bible, notation, voice identity and accessibility | Motion designer/operator |
| Renderer and media | Components, compiler, timing, captions and cache | Media/frontend engineer |
| Agent tasks | Contracts, prompts/providers, evaluations and fallbacks | AI/backend engineer |
| Workflow and control | Durable execution, approvals, retries and revision graph | Backend engineer |
| Studio experience | Review, preview, scene edits, package and runs | Frontend engineer |
| Data and provenance | Versioned records, rights, artifacts and migrations | Backend/data engineer |
| Distribution | Account preflight, OAuth, release and reconciliation | Integrations engineer |
| Audience learning | Metric definitions, baselines and experiments | Data/product owner |
| Security and operations | Access, credentials, delivery, backups and monitoring | Platform/backend engineer |
| Quality and commercial learning | Verification, effort/cost baseline and paid interviews | QA/product owner |

Use one GitHub repository with Studio, API/domain, workflow workers, media workers, generated shared contracts, scene library, fixtures/evaluations and deployment configuration. Maintain the PRD, motion bible, short architecture decisions, contracts/API/schema, workflow/revision specification, task/evaluation definitions, delivery cards and operating runbook.

Project board states are Backlog, Ready, In progress, Review, Verified and Done, with a visible Blocked reason. Limit each implementer to one main engineering card. Merge small dependency-complete changes. Weekly review covers accepted behavior/videos, actual effort, costs, failures, unresolved risks and the next gate.

## 24 Engineering handoff backlog

Preserve the existing OOS identifiers. These are seed cards to refine with owners, estimates, permitted files, dependencies, persona/story IDs, FR/CR coverage and verification evidence. They are not completed tasks. Cards 020–023 refine shared work and must not be double-counted.

| Card | Deliverable | Dependencies | Completion evidence |
|---|---|---|---|
| OOS-001 | Scope and decision register | None | Releases, capacity, budget and pending decisions recorded |
| OOS-002 | Twelve briefs and first three topics | 001 | Four-series coverage, claims, visual needs and reviewer |
| OOS-003 | Motion and voice references | 002 | Original theme, notation, persistent colors/objects and voice sample |
| OOS-004 | Rights and channel preflight | 001 | Tested capability/license matrix and fallback routes |
| OOS-005 | Scene contract and fixtures | 002,003 | Types, object/action IDs, calculations, timing and invalid cases |
| OOS-006 | Six animation families | 005 | Original vertical story with correct values and continuity |
| OOS-007 | Voice and captions | 004,006 | Measured alignment, pronunciation and readability |
| OOS-008 | Scene revision and cache | 007 | Actual reuse and invalidation demonstrated |
| OOS-009 | Repository and CI | 005 | Checks, schema generation, fixtures and render smoke |
| OOS-010 | Versioned persistence | 008,009 | Scoped records, immutable assets and migrations |
| OOS-011 | Durable execution | 010 | Restart, bounded retries, timeout and cancellation |
| OOS-012 | Approval and cost reservation | 011 | Stale authority rejected and dispatch budget enforced |
| OOS-013 | Research and claim ledger | 012 | Contradictions visible and unsupported claims blocked |
| OOS-014 | Script and storyboard tasks | 013 | Story beats, persistent objects and supported action output |
| OOS-015 | Evidence and scene review UI | 014 | Operator edits/reviews without code changes |
| OOS-016 | QA and final package UI | 015 | Master, captions, metadata, rights, costs and sources linked |
| OOS-017 | Manual publication and feasible adapter | 004,016 | Destination/version recorded and uncertainty handled |
| OOS-018 | Twelve-video quality gate | 016,017 | Reviewed 4/4/2/2 slate with public records and costs |
| OOS-019 | Metrics and first experiment | 018 | Baseline/missing-data handling and prospective loop |
| OOS-020 | Verified model and action timeline | 005 | Correct domains, values/counts and rejected invalid actions |
| OOS-021 | Continuity and revision fixtures | 006,008,020 | Changed state/timing invalidates correct dependents |
| OOS-022 | Phrase-to-action alignment | 007,020 | Measured synchronization and readable equation holds |
| OOS-023 | Versioned publication package | 012,016 | Package, destination, metadata and approval remain linked |
| OOS-024 | Connected upload and reconciliation | 004,017,023 | Private transfer where supported, external ID, readiness and recovery |
| OOS-025 | Scheduling and cancellation | 024 | Future timezone-safe schedule and confirmed external cancellation |
| OOS-026 | Publication verification | 017,023 | Manual/connected outcome, actual URL/status and partial checks visible |
| OOS-027 | Full lifecycle demonstration | 018,020–023,026 | Original traced from idea to verified channel record |

Cards 020–022 belong to the animation spike; 023 to the Studio/package work; the manual part of 026 to M5. Cards 024–025 and connected verification in 026 are R3 unless separately estimated earlier. Demonstrate 027 manually at R2 and repeat through the adapter at R3.

For coding-agent handoff, provide one bounded card, current baseline, relevant contracts, acceptance criteria and permitted change scope. Review the diff and actual behavior before merging. This PRD defines product behavior; it is not a substitute for API specifications, migrations, scene schemas, task contracts or architecture decisions.

## 25 Risks and responses

| Risk | Impact | Required response |
|---|---|---|
| Generic/repeated output | Poor audience value and possible platform problems | Original narrative/visual review and full-slate variety checks |
| Incorrect facts or visuals | Misleads viewers and undermines trust | Claim evidence, verified models and appropriate human review |
| Unsupported animation | Topic cannot be explained faithfully | Capability preflight, simplify honestly or add a reviewed component |
| API/access restriction | Distribution or measurement unavailable | Early account probes, explicit capability labels and manual fallback |
| Cost escalation | Unsustainable operation or margins | Vector-first output, budget reservation, cache and bounded retries |
| Sparse audience data | False preference/optimization conclusions | Cold-start labels, exploration and comparable uncertainty-aware reporting |
| Render-library complexity | Schedule slips and high maintenance | Small proven families and established underlying renderers |
| Lost upload/release acknowledgement | Duplicate posts or unauthorized action | Transfer/external-ID reconciliation and unknown-state handling |
| Rights/credential exposure | Unusable assets or compromised accounts | Rights ledger, restricted credentials and revocation/deletion controls |
| Creator churn or weak demand | Subscription model fails | Qualified paid pilots, repeat-use evidence and cancellation learning |
| Heavy review/support | Low operational efficiency | Measure human work, improve repairs and constrain scope |
| Incumbent replication | Weak differentiation | Distinctive outputs, reliable revision and validated customer utility |

## 26 Open decisions and change control

The clarified product direction is original narrated mathematical/scientific visual storytelling inside the broader four-layer platform. It is a requirements baseline for planning; commercial and provider decisions below remain open. Record owner, evidence, decision date and consequences when each closes.

| Decision | Current position | Due |
|---|---|---|
| DEC-01 Brand/channel naming | OpportunityOS platform and Signal Motion working engine name; original channel identity to choose | Before public identity is finalized |
| DEC-02 Editorial niche and first briefs | Broad adjacent STEM/technology promise; mathematical feasibility case first | M0 |
| DEC-03 Capacity and launch date | January channel target can use a smaller manual-distribution launch | Before calendar commitment |
| DEC-04 Review authority and quality thresholds | Named reviewers; proposed rubric and 10-of-12 reliability threshold to adopt/calibrate | M0 and before R2 judging |
| DEC-05 Budget | Monthly/per-video ceilings and cost treatment unconfirmed | Before paid provider execution scales |
| DEC-06 Voice/model/asset providers | Rights, pronunciation, quality and cost tests required | M1 |
| DEC-07 Renderer and runtime | Proposed Remotion/FFmpeg and Temporal; optional Manim based on sample | M1/M2 architecture decisions |
| DEC-08 Platform capability | YouTube first where authorized; Instagram after verified eligibility/access | Before enabling each adapter |
| DEC-09 Initial primary metric | Select an available attention measure and window with explicit cold-start status | Before first measured publication |
| DEC-10 Buyer and price | Creator versus studio willingness to pay and sustainable quotas unproven | Before R4 investment |
| DEC-11 Growth allocation | Reallocate from repeated evidence while preserving exploration | After R2 and during the study |
| DEC-12 Business expansion | One vertical, first-party integrations and evidence threshold to select | Before R5 investment |

Changes affecting requirements, release scope, review authority or acceptance thresholds must state the affected IDs, rationale, migration/review impact and owner. Update this baseline rather than leaving contradictory appendices. Future budgets, app permissions, subscriptions and public actions require their own applicable authority; a PRD does not execute them.

## 27 Source consolidation and references

### 27.1 Consolidation record

| Source | Preserved contribution | Resolution in this version |
|---|---|---|
| OpportunityOS v1 PDF dated 22 October 2026 | Vision, customers, four layers, journeys, production/audience/business scope, commercialization and risks | Integrated into Sections 1–6 and 14–26 |
| Overall PRD v1.1 | FR-01–18, CR-01–10, editorial portfolio, Opportunity Lab, metrics and conditional growth experiment | Identifiers retained; gates/counting clarified in Sections 4, 11–12 and 17–19 |
| Development Plan document revision 1.1 | Release sequence, workflow contracts, lifecycle, worked example, estimates, owners and OOS-001–027 | Consolidated into Sections 7–10 and 14–26 |
| User examples and clarifications | Dark/color-coded mathematical visuals, persistent objects, meaningful animation and a story | First six families and original reference storyboard in Sections 5 and 9–10 |

Earlier drafts variously used 10 concepts, twelve briefs, a generic six-component spike and an AI-only first-channel example. This baseline uses twelve discovery briefs, six visual-storytelling families, one mathematical feasibility story and the broader channel promise. It retains the twelve-video/four-series validation before the conditional growth study. The first production/export milestone is distinct from full distribution automation and paid SaaS.

The persona/story expansion adds six design personas, a viewer profile, role boundaries, US-01–26 and eight expanded journeys. These derive from the product scope and are not claims of completed interviews. Existing FR/CR identifiers, release gates and development cards retain their authority and scope.

### 27.2 Public implementation references

Documentation was reviewed during planning on 12 November 2026. Re-check current terms, fields and actual account capabilities when implementing. No account connection or vendor approval is implied.

- **S1** [YouTube Data API revision history](https://developers.google.com/youtube/data/revision_history)
- **S2** [YouTube video upload reference](https://developers.google.com/youtube/data/reference/rest/v3/videos/insert)
- **S3** [YouTube video status processing and scheduling](https://developers.google.com/youtube/data/reference/rest/v3/videos)
- **S4** [YouTube resumable uploads](https://developers.google.com/youtube/data/guides/using_resumable_upload_protocol)
- **S5** [YouTube Analytics channel reports](https://developers.google.com/youtube/analytics/channel_reports)
- **S6** [YouTube originality and monetization policies](https://support.google.com/youtube/answer/1311392)
- **S7** [YouTube altered and synthetic content disclosure](https://support.google.com/youtube/answer/14328491)
- **S8** [Meta official Instagram API workspace](https://www.postman.com/meta/instagram/overview)
- **S9** [Meta Reels publishing route](https://www.postman.com/meta/instagram/folder/y6xustx/reels-publishing)
- **S10** [Remotion licensing and pricing](https://www.remotion.dev/docs/license/pricing)
- **S11** [Remotion terms](https://www.remotion.dev/docs/terms)
- **S12** [Temporal Python SDK](https://docs.temporal.io/develop/python)
- **S13** [Temporal workflow replay](https://docs.temporal.io/workflows)
- **S14** [Manim animation reference](https://docs.manim.community/en/stable/reference_index/animations.html)

Platform-native disclosures depend on the actual media and applicable rules. Meta's public route did not expose enough accessible detail during planning to establish account-specific permissions. Remotion eligibility depends on the licensed entity and use case; do not assume SaaS automatically requires paid licensing or that a small project automatically qualifies. These remain implementation preflight items.
